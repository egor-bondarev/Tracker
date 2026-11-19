"""Install a digest-selected Tracker release or restore its previous healthy version."""

import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from check_tracker import check_tracker


CONFIG = Path("/etc/tracker-deploy")
STATE = Path("/var/lib/tracker-deploy")
SOURCE = "https://github.com/egor-bondarev/Tracker.git"
PREFIX = "ghcr.io/egor-bondarev/tracker-"
SERVICES = {"record": "record_service", "analytics": "analytic_service", "web": "web"}
DOCKER = [
    "/usr/bin/docker", "--host", "unix:///var/run/docker.sock",
]
COMMAND_ENV = {
    "PATH": "/usr/bin:/bin",
    "HOME": "/root",
    "DOCKER_CONFIG": str(CONFIG / "docker"),
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_TERMINAL_PROMPT": "0",
}


def run(args, *, capture=False, timeout=120, env=None):
    return subprocess.run(
        args, check=True, text=True, stdout=subprocess.PIPE if capture else None,
        env=COMMAND_ENV if env is None else env, timeout=timeout,
    ).stdout


def release_for(sha, digests):
    if not re.fullmatch(r"[a-f0-9]{40}", sha):
        raise ValueError("Expected a full Tracker commit SHA.")
    if len(digests) != len(SERVICES) or any(
        not re.fullmatch(r"sha256:[a-f0-9]{64}", digest) for digest in digests
    ):
        raise ValueError("Expected one sha256 digest for each Tracker image.")
    return {"revision": sha, "images": {
        key: PREFIX + key + "@" + digest for key, digest in zip(SERVICES, digests)
    }}


def require_current_main(sha):
    ref = run(
        ["/usr/bin/git", "ls-remote", "--exit-code", SOURCE, "refs/heads/main"],
        capture=True, timeout=15,
    )
    if ref.split() != [sha, "refs/heads/main"]:
        raise ValueError("Automatic deployment skipped because main has moved.")


def check_ready(attempts=12):
    for attempt in range(attempts):
        report = check_tracker("http://127.0.0.1:8080", "http://127.0.0.1:8000", timeout=2)
        if report["ok"]:
            return
        if attempt + 1 < attempts:
            time.sleep(2)
    raise RuntimeError("Tracker health checks failed: " + json.dumps(report["checks"]))


def write_state(state):
    with tempfile.NamedTemporaryFile(mode="w", dir=STATE, delete=False) as file:
        temporary = Path(file.name)
        try:
            json.dump(state, file, indent=2)
            file.flush()
            os.fsync(file.fileno())
            temporary.replace(STATE / "releases.json")
        finally:
            temporary.unlink(missing_ok=True)


def load_state():
    path = STATE / "releases.json"
    if path.exists():
        return json.loads(path.read_text())

    # Record the actual images of the already deployed, healthy Acer stack.
    check_ready(attempts=1)
    images = {}
    for key, service in SERVICES.items():
        image_id = run(
            DOCKER + ["inspect", "--format", "{{.Image}}", f"tracker-{service}-1"],
            capture=True,
        ).strip()
        if not re.fullmatch(r"sha256:[a-f0-9]{64}", image_id):
            raise RuntimeError(f"Unable to find the running {service} image.")
        tag = f"tracker-local-{key}:{image_id[7:]}"
        run(DOCKER + ["tag", image_id, tag])
        images[key] = tag
    state = {"current": {"revision": "pre-automation", "images": images}, "previous": None}
    write_state(state)
    return state


def prepare(release):
    for image in release["images"].values():
        if image.startswith(PREFIX):
            run(DOCKER + ["pull", image], timeout=180)
            revision = run(DOCKER + [
                "image", "inspect", "--format",
                '{{index .Config.Labels "org.opencontainers.image.revision"}}', image,
            ], capture=True).strip()
            if revision != release["revision"]:
                raise ValueError("Image revision does not match the requested Tracker commit.")
        else:
            run(DOCKER + ["image", "inspect", "--format", "{{.Id}}", image], capture=True)


def apply(release):
    env = COMMAND_ENV | {
        f"TRACKER_{name.upper()}_IMAGE": image for name, image in release["images"].items()
    }
    run(DOCKER + [
        "compose", "--project-name", "tracker", "--project-directory", str(CONFIG),
        "--env-file", str(CONFIG / "tracker.env"), "-f", str(CONFIG / "compose.yml"),
        "up", "-d", "--no-deps", "--no-build", "--pull", "never", *SERVICES.values(),
    ], env=env)
    check_ready()


def install_release(state, candidate, *, auto=False):
    current = state["current"]
    if candidate == current:
        check_ready()
        print("This release is already active and healthy.")
        return
    prepare(candidate)
    if auto:
        require_current_main(candidate["revision"])
    # Both versions must be available locally before touching running services.
    for image in current["images"].values():
        run(DOCKER + ["image", "inspect", "--format", "{{.Id}}", image], capture=True)
    write_state({**state, "pending": candidate})
    try:
        apply(candidate)
        write_state({"current": candidate, "previous": current})
    except (OSError, RuntimeError, subprocess.SubprocessError) as deploy_error:
        print("Release failed. Restoring the version active before the request.", file=sys.stderr)
        try:
            apply(current)
            write_state(state)
        except (OSError, RuntimeError, subprocess.SubprocessError) as rollback_error:
            raise RuntimeError("Deployment and recovery both failed. Check Acer locally.") from rollback_error
        raise RuntimeError("Release failed. The prior version is healthy again.") from deploy_error
    print("Active healthy release:", candidate["revision"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    deploy = commands.add_parser("deploy")
    deploy.add_argument("mode", choices=("auto", "manual"))
    deploy.add_argument("revision")
    deploy.add_argument("digests", nargs=3)
    commands.add_parser("rollback")
    args = parser.parse_args()
    if os.geteuid() != 0:
        parser.error("run the installed release controller with sudo")
    try:
        candidate = release_for(args.revision, args.digests) if args.action == "deploy" else None
        with (STATE / "deploy.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            state = load_state()
            if "pending" in state:
                print("An interrupted deployment was found. Restoring the last healthy release.")
                apply(state["current"])
                state.pop("pending")
                write_state(state)
            if args.action == "rollback":
                candidate = state["previous"]
                if candidate is None:
                    raise ValueError("There is no previous healthy release to restore yet.")
            install_release(state, candidate, auto=args.action == "deploy" and args.mode == "auto")
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
