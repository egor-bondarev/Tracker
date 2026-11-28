# Tracker desktop

Small timer window (Tauri 2 + React) for Windows and macOS. It replaced the earlier
PyQt window (`desktop_gui/`, see git history).

## How it works

- **Start / stop** write the task to a local `tasks.json` first, then send it in the
  background to `PUT <server>/api/tasks/by-client-id/<uuid>`. Each task gets its UUID
  on the client, so resending never creates duplicates.
- **Offline**: if the server does not answer within 4 seconds the task stays in
  `tasks.json`, and a red dot in the top bar shows how many records are not sent.
  Sync is retried on start, after each action, on the interval from the settings
  (hourly by default) and from the menu (*Синхронизировать*, which also retries
  records the server rejected).
- **Settings** (server address, token, sync interval) live in `settings.json`. Both files are
  in the app data directory: `%APPDATA%\io.github.egorbondarev.tracker\` on Windows,
  `~/Library/Application Support/io.github.egorbondarev.tracker/` on macOS.
- **One address**: the server address is the web UI, e.g. `http://192.168.0.38:8080`.
  nginx proxies the record API under `/api`; *Открыть аналитику* opens the address.
- **Token**: every record API call except `/api/ready` sends
  `Authorization: Bearer <token>`, and each user sees only their own tasks and
  categories. The token is issued by the server admin command, one per user, and is
  entered once in *Настройки* (stored in plain text in `settings.json`).
  *Проверить* checks the address (`/api/ready`) and then the token
  (`/api/tasks/active`). Without a token the window opens on the settings screen. If
  the server answers 401/403, sending stops and the queued records stay in
  `tasks.json` untouched (not flagged as rejected); the red dot and the menu say
  *Проверь токен*, and the next sync after the token is fixed sends them.
- **Import from the old version**: pick the folder with the old `YYYY-MM-DD.json`
  files. Times get their date from the file name (a finish before the start moves to
  the next day), categories are created by name, and each record gets a UUID derived
  from its content, so importing the same files again adds nothing. Records go to the
  user whose token is in the settings.

## Development

Requires Node 20+ and Rust (stable).

```bash
npm ci
npm test              # api, queue, sync and legacy import logic
npx tauri dev         # run the window against a running server
npx tauri build       # installers in src-tauri/target/release/bundle/
```

CI (`.github/workflows/desktop.yml`) builds Windows (`.exe`, `.msi`) and macOS (`.dmg`)
installers as workflow artifacts. Neither is signed with a paid developer identity, so
the first launch asks for confirmation:

- **macOS**: the app is signed ad hoc (`bundle.macOS.signingIdentity: "-"`). macOS says
  it cannot verify the developer; allow it in *System Settings → Privacy & Security →
  Open Anyway*. Without that signature macOS reports the downloaded app as "damaged".
- **Windows**: SmartScreen shows *More info → Run anyway*.

On macOS the window also needs **Local Network** access to reach a server in the home
network: allow it when asked, or later in *System Settings → Privacy & Security →
Local Network*. Without it the settings check reports "Сервер не отвечает" although
the same address opens in a browser.

Keep one copy of the app per Mac: a local `tauri build` leaves another `Tracker.app`
with the same bundle id in `src-tauri/target/release/bundle/`, and macOS may launch that
one instead of the installed app.
