# A1OS

Autonomous multi-engine AI/agent orchestration platform ("A1OS Factory"). Python monolith (`core/`, `infra/`, `api/`) plus Node tooling and productized "OS" packages under `products/`. The active product is `products/education-os` (Little Oaks Education OS): its own FastAPI app at `products/education-os/api/app.py` backed by SQLite `education.db`. Remote: `git@github.com:BudBudness/A1OS.git`, working copy on branch `main`.

## Environment

- Repo lives under Termux on Android: `/data/data/com.termux/files/home/A1OS_RESTORED`. Two pythons coexist:
  - Termux `/data/data/com.termux/files/usr/bin/python3` (3.14.6) — has pytest 9.1.1 and project deps; runs the live services.
  - The `python3` on PATH (PRoot/Ubuntu, 3.14.4) has **no pytest/FastAPI** — `python3 -m pytest` fails there. Use the Termux interpreter or `pip install -r requirements.txt` first.
- Scripts use Termux shebangs, e.g. `#!/data/data/com.termux/files/usr/bin/bash`.
- Push auth is **HTTPS via `gh`** (account `BudBudness`, `gh auth setup-git` in the Termux HOME). The remote is `https://github.com/BudBudness/A1OS.git`. The SSH pubkey is *not* registered on GitHub, so run `git` with `HOME=/data/data/com.termux/files/home` (or `gh auth login`) — an SSH push will fail with `Permission denied (publickey)`.

## Commands

- Tests: `python3 -m pytest` (pytest.ini `asyncio_mode=auto`; asyncio handling in `tests/conftest.py`). CI equivalent: `python -m compileall .` and `python -m unittest discover tests`.
- Root-level `*_test.py` (e.g. `authorization_lifecycle_integrity_test.py`) are standalone async scripts — run directly with `python3 <file>.py`.
- Core API: `python3 main.py` → uvicorn on :3011 (`core/api.py`).
- Control CLI: `./a1ctl status` / `./a1ctl exec` — talks to the core on `http://127.0.0.1:3011/v1`.
- education-os API: `cd products/education-os/api && python3 -m uvicorn app:app --host 127.0.0.1 --port 3012`.
- Node tooling (`package.json`: playwright, chrome-remote-interface, react-three): `npm install`.

## Runtime wiring (production topology)

Canonical launch: `education-os-launch.sh` (Termux home; tracked source of truth `ops/education-os-launch.sh` — keep the two in sync, e.g. `cp ops/education-os-launch.sh ~/`). One service per port — do not move these:

- **3011** — A1OS core engine (`python3 main.py`). Running and supervised by the watchdog; edu owns 3012.
- **3012** — education-os API (`run-production.sh` → `uvicorn api.app:app --host 127.0.0.1 --port 3012 --workers 1 --proxy-headers`).
- **8080** — frontend + same-origin `/api` proxy (`products/education-os/web/server.py` serves `products/education-os/web`, proxies to 3012).
- **Cloudflare tunnel `a1os-prod`** (`~/.cloudflared/config.yml`) — `little-oaks.pyongcity.org/api/*` → 3012, everything else → 8080.
`a1ctl` talks to the core on 3011 (runs `python3 main.py`).

Watchdogs + cron (canonical source `~/crontab.txt`; installed to BOTH the `u0_a433` spool that crond reads and the `root` spool that proot `crontab -l` shows): hourly `ops/a1os-production-watchdog.sh` (core :3011, API :3012, frontend :8080, public tunnel, DB integrity; auto-restarts core/API/web/tunnel — tunnel relaunched as `cloudflared tunnel --config ~/.cloudflared/config.yml run a1os-prod`, kill patterns scoped to `a1os-prod`/its UUID `7fdd3dce` so other tunnels are never touched), daily 1:00 + weekly Sun 12:00 (local EAT) DB backups via `~/backup-little-oaks-education-db.sh` (tracked source `ops/backup-little-oaks-education-db.sh`; sqlite `.backup`, integrity-checked, 30-day retention). The watchdog fires a **ntfy.sh alert** on any FAIL/CRITICAL — topic read from `~/.a1os/ntfy.topic` (untracked; subscribe in the ntfy app to receive pushes). After each DB backup, `ops/push-education-backups.sh` copies the latest `education-*.db` into the **private** GitHub repo `BudBudness/a1os-backups` (local clone `~/a1os-backups`, HTTPS/`gh` auth, idempotent). Auth: `POST /auth/change-password` (authed; requires `current_password` + `new_password`, min 8 chars; invalidates other sessions); UI has a Change Password page + Logout in the sidebar. `/auth/login` and `/auth/change-password` are rate-limited (20 attempts / 300s per client IP, in-memory — keep uvicorn at `--workers 1`).

## Gotchas

- `.env` in repo root holds secrets (Cloudflare tokens, `SECRET_KEY`, `JWT_SECRET_KEY`). Never print or commit it.
- `products/education-os/deployments/little-oaks/data/education.db` is a tracked binary (`.gitignore` ignores `*.db`; this one was force-added) with local modifications. Release and acceptance pipelines depend on it — don't rebuild or drop it casually.
- `./little-oaks-release.sh` runs Stage 4–7 acceptance suites, backs up the DB, commits, tags, and **pushes to origin main**. Don't run casually.
- `data/a1os.db-shm` and `data/a1os.db-wal` are untracked SQLite WAL sidecars (covered by `*.db-shm`/`*.db-wal`); a live engine rewrites them, so ignore any `git status` noise from them.
- `infra/` (redis/nats/postgres/minio/k8s) and `deployment/docker-compose.yml` are **planned, aspirational scaffolding — not load-bearing**. The live product runs as two Termux processes (uvicorn :3012 + web-server :8080) behind the Cloudflare tunnel. Don't treat infra as the deployment target.
- Frontend server: single source of truth is the tracked `products/education-os/web/server.py` (`ThreadingHTTPServer`, portable `WEB` path). The watchdog's `restart_web` launches it directly. The old untracked `~/education-os-web-server.py` was retired — don't reintroduce it.
- The watchdog holds a flock on fd 9 (`.locks/production-watchdog.lock`). Its restart functions MUST close fd 9 in spawned children (`9>&-`) — otherwise the long-running child (core/API/web) inherits the lock fd and silently deadlocks every later watchdog run (`flock -n || exit 0`). If `logs/production-watchdog.log` stops growing, check `ls -l /proc/<pid>/fd/9` for the holder.
- Cron gotchas: the runit service `crond` ships DISABLED (`down` file) — if `ps` shows no `crond -n` process, run `sv up crond` (it must be up for any scheduled job to fire). crond runs as the real Termux uid `u0_a433` and ONLY reads `$PREFIX/var/spool/cron/u0_a433`; inside PRoot, `crontab` writes to the `root` spool which crond ignores. Always install to both (copy `~/crontab.txt` to `.../spool/cron/u0_a433` AND run `crontab ~/crontab.txt`).
- Host memory is tight (~5.5Gi total, ~1.1Gi free) — avoid parallel heavy builds.
