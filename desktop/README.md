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
- **Settings** (server address, sync interval) live in `settings.json`. Both files are
  in the app data directory: `%APPDATA%\io.github.egorbondarev.tracker\` on Windows,
  `~/Library/Application Support/io.github.egorbondarev.tracker/` on macOS.
- **One address**: the server address is the web UI, e.g. `http://192.168.0.38:8080`.
  nginx proxies the record API under `/api`; *Открыть аналитику* opens the address.
- **Import from the old version**: pick the folder with the old `YYYY-MM-DD.json`
  files. Times get their date from the file name (a finish before the start moves to
  the next day), categories are created by name, and each record gets a UUID derived
  from its content, so importing the same files again adds nothing.

## Development

Requires Node 20+ and Rust (stable).

```bash
npm ci
npm test              # queue, sync and legacy import logic
npx tauri dev         # run the window against a running server
npx tauri build       # installers in src-tauri/target/release/bundle/
```

CI (`.github/workflows/desktop.yml`) builds unsigned Windows (`.exe`, `.msi`) and macOS
(`.dmg`) installers as workflow artifacts. Unsigned builds trigger a SmartScreen /
Gatekeeper warning on first launch.
