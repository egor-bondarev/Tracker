# Releases to Acer

Tracker is public. Use GitHub-hosted workers for tests and image builds. Register
the Acer runner in a separate **private** repository with trusted maintainers
only. The runner never checks out Tracker or runs scripts from release branches.
It sends validated image digests to a root-owned release controller. The runner
does not need membership in the Docker group, SSH credentials, or inbound access
from GitHub.

The controller updates only the web, record, and analytics services on the
existing `tracker_default` network. PostgreSQL, its volume, and the dashboard
continue to run independently. Database migrations and database restores are
outside this release flow. Releases must be compatible with the live schema.
The project name, LAN addresses, and ports remain compatible with dashboard
checks. Use this rollout method for the application containers after enabling it
and coordinate any separate manual Compose operations.

## GitHub settings

1. Create a private repository, for example `tracker-deploy-control`. Create its
   `main` branch and copy [acer-deploy.yml](control-repo/acer-deploy.yml) into
   `.github/workflows/acer-deploy.yml` on that branch. Keep the repo private and
   limit who can edit its workflows or invoke the runner.
2. Create a fine-grained personal access token restricted to the private control
   repository with repository permission **Actions: Read and write**.
3. In the public Tracker repository, create the environment `acer-dispatch`.
   Under its deployment branch rules, allow only the `main` branch. In that
   environment add these entries.

   | Kind | Name | Value |
   | --- | --- | --- |
   | Secret | `ACER_DISPATCH_TOKEN` | The restricted token from step 2 |
   | Variable | `ACER_CONTROL_REPO` | The private repository in `owner/repo` form |

4. In Tracker, leave the **repository variable** `ACER_AUTO_DEPLOY` unset or
   `false` until the first manual deploy and rollback have been verified.
   To limit automatic releases to reviewed changes, protect `main` and require
   pull requests. The workflow responds to pushes that advance `main`, including
   merge commits and fast-forward merges.

Use GitHub's built-in `GITHUB_TOKEN` for publishing images. After the first
publish, verify that the three GHCR packages `tracker-record`,
`tracker-analytics`, and `tracker-web` contain only the public application code.
Set them to **public** so Acer can pull the digest references without credentials.
PostgreSQL passwords stay in the host's local configuration. They are not
required in GitHub. A private registry alternative requires a separately managed
read-only registry credential on Acer.

## Prepare Ubuntu on Acer

Use a reviewed checkout of this change for installation. Keep the production
Tracker stack running during setup. Install the controller and a copy of the
production Compose configuration in directories owned by root. The example
assumes the live Tracker checkout is `~/apps/Tracker` on the Acer's Ubuntu user.

```bash
sudo install -d -m 0755 /usr/local/libexec/tracker-deploy
sudo install -d -m 0700 /etc/tracker-deploy /var/lib/tracker-deploy
sudo install -o root -g root -m 0644 deployment/acer/tracker_release.py \
  scripts/check_tracker.py /usr/local/libexec/tracker-deploy/
sudo install -o root -g root -m 0755 deployment/acer/tracker-release /usr/local/sbin/tracker-release
sudo install -o root -g root -m 0644 deployment/acer/compose.release.yml /etc/tracker-deploy/compose.yml
sudo install -o root -g root -m 0600 ~/apps/Tracker/.env /etc/tracker-deploy/tracker.env
```

The controller passes only the application DB name, user, and password to the two
API containers. The admin password is not passed. Review the installed ports if
the existing setup differs from the defaults (Record 8000, analytics 8001, web
8080). The health check uses Record 8000 and web 8080 on loopback.

Create a dedicated Ubuntu user `tracker-runner` outside the `docker` and `sudo`
groups. Install and configure the Linux x64 self-hosted runner from **Settings →
Actions → Runners** of the **private control repository**, using the generated
registration command and the label `acer-deploy`. Run it as `tracker-runner`
and install its service with `sudo ./svc.sh install tracker-runner`, then
`sudo ./svc.sh start`. Keep the registration token local. The runner service
starts with Ubuntu through the existing WSL startup setup.

Grant only these two commands via `sudo visudo -f /etc/sudoers.d/tracker-release`.

```sudoers
tracker-runner ALL=(root) NOPASSWD: /usr/local/sbin/tracker-release deploy *, /usr/local/sbin/tracker-release rollback
```

The installed controller validates both the operation and its arguments. All
deployment files and its state directory must remain writable only by root.
Never point this rule to a checkout or a file owned by the runner.

## Verify the release and recovery paths

On merging this change, the new release workflow will appear in Tracker's
Actions tab. Run **Tracker release for Acer** from the workflow branch `main`.
Keep `source_branch=main` and set **publish_only** for the first run. After the
packages are public, run again with **publish_only** cleared. A branch you
explicitly trust can also be entered as `source_branch`. It must pass the same
tests and remain compatible with the live DB. The run prints where to find the
deployment status in the private control repository.

On a successful request, verify Tracker from the Mac and check the corresponding
run in the private repo. To test a manual rollback, run **Deploy or roll back
Tracker on Acer** from the private `main` branch with **operation=rollback**.
The other inputs stay empty. It swaps the current and previous healthy releases
after checking the restored version. Run a new manual deploy before enabling
`ACER_AUTO_DEPLOY=true` if you want the latest build active.

A release is recorded only after all three Tracker checks pass. When a release
fails its checks, the controller restores the last healthy images and reports the
failed deployment. It records an in-progress change before replacing containers
so another invocation can recover an interrupted deploy. The first run tags the
images of the currently healthy Tracker as its rollback baseline. Keep those
images and the last healthy remote image digests available for rollback. Review
the previous version's compatibility before making future database changes.
