# Tracker API in Bruno

A [Bruno](https://www.usebruno.com/) collection with every Tracker request: the
record API (proxied under `/api` by the web server) and the analytics GraphQL
endpoint. Open this folder in the Bruno app, or run it from the terminal with the
pinned Bruno CLI.

| Folder  | What it does | Where to run it |
|---------|--------------|-----------------|
| `read`  | Readiness, running task, categories, GraphQL tasks of today and categories | Any server |
| `write` | Create a category → start → finish → read → edit a task → record without start → sync by client id twice (no duplicate) → delete the tasks → rename and archive the category | Local stack only |

`write` leaves no tasks behind, but categories cannot be deleted through the API:
each run leaves one archived `bruno-<time>` category.

Environments: `local` (`http://127.0.0.1:8080`) and `acer` (`http://192.168.0.38:8080`).

## Terminal

```bash
cd bruno
npm ci
npx bru run read --env acer
npx bru run write --env local
npx bru run "read/Tasks in period.bru" --env acer
```

Override a variable for one run, for example another server:

```bash
npx bru run read --env local --env-var baseUrl=http://10.0.0.5:8080
```

Add `--reporter-json results.json` to keep the responses.

## Variables

The collection script sets `now` and `today` (server time format
`YYYY-MM-DD HH:MM:SS`), `runTag` (unique name prefix) and `clientId` (UUID for
the sync endpoint) before each request. `write` requests save `categoryId`,
`taskId`, `recordedTaskId` and `syncedTaskId` for the requests after them.
