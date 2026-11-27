# Tracker

## Calling the API: use the Bruno collection

The Bruno collection in [bruno/](bruno/README.md) is the single place for manual
Tracker API calls (record API under `/api`, analytics at `/graphql`).

- **Use it instead of direct URL calls.** For manual or exploratory requests run the
  collection, not `curl`, `httpie`, Python `requests`/`urllib` or `fetch` with
  hand-written URLs:

  ```bash
  cd bruno && npm ci
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

Automated tests and code (`record_service/tests`, `tests/`, `scripts/`, `desktop/`)
keep their own HTTP clients; this rule is about calls made by hand or by an agent.
