# Tracker

## Calling the API: use the Bruno collection

The Bruno collection in [bruno/](bruno/README.md) is the only way to call the
Tracker API by hand (record API under `/api` or ports 8000/8001, analytics at
`/graphql`, including `/ready` and `/openapi.json`).

- **Direct API calls are forbidden.** Do not send requests to a Tracker server with
  `curl`, `wget`, `httpie`, Python `requests`/`urllib`, `fetch`, a browser or
  DevTools, or with ad-hoc scripts and temporary tests written for the occasion,
  against any environment (local, Acer, CI). Use the collection:

  ```bash
  cd bruno && npm ci   # once; the token of a Tracker user goes into bruno/.env (TRACKER_TOKEN)
  npx bru run read --env acer
  npx bru run "read/Tasks in period.bru" --env local
  ```

- **Missing request? Add it first.** If a call you need is not in the collection,
  add a `.bru` request (with assertions) and run that request.
- **Keep it current in the same change.** When an endpoint, request body, query
  parameter or response changes, update the matching `.bru` files and their
  assertions in the same commit; add requests for new endpoints.
- **Folder rules.** `read/` holds read-only requests only. `write/` holds requests
  that change data, run in order and clean up after themselves; save ids for later
  requests with `bru.setVar` instead of hard-coding them.
- **Never run `write/` against `acer`** (real data). Against Acer use `read/` or a
  single read-only request.
- **Verify after changing the API or the collection**, against the local stack:
  `npx bru run read --env local` and `npx bru run write --env local`.

Allowed without Bruno:

- **Database access** (`psql` in the PostgreSQL container, `docker compose exec`,
  Alembic, the `python -m tracker_db.users` admin command).
- **The project's committed tools and test suites**, run as they are: the
  `record_service` tests, `tests/` (including `deployment_smoke.py`),
  `scripts/check_tracker.py`, the desktop app and its tests, CI workflows.
  Their HTTP clients are part of the code; this rule covers calls made by hand or
  by an agent.
