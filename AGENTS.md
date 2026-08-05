# A1OS

Autonomous multi-engine AI/agent orchestration platform ("A1OS Factory"). Python monolith (`core/`, `infra/`, `api/`) plus Node tooling and productized "OS" packages under `products/`. The active product is `products/education-os` (Little Oaks Education OS): its own FastAPI app at `products/education-os/api/app.py` backed by SQLite `education.db`. Remote: `git@github.com:BudBudness/A1OS.git`, working copy on branch `main`.

## Environment

- Repo lives under Termux on Android: `/data/data/com.termux/files/home/A1OS_RESTORED`. Two pythons coexist:
  - Termux `/data/data/com.termux/files/usr/bin/python3` (3.14.6) — has pytest 9.1.1 and project deps; runs the live services.
  - The `python3` on PATH (PRoot/Ubuntu, 3.14.4) has **no pytest/FastAPI** — `python3 -m pytest` fails there. Use the Termux interpreter or `pip install -r requirements.txt` first.
- Scripts use Termux shebangs, e.g. `#!/data/data/com.termux/files/usr/bin/bash`.
- No SSH key in `~/.ssh` — `git push` to GitHub fails.

## Commands

- Tests: `python3 -m pytest` (pytest.ini `asyncio_mode=auto`; asyncio handling in `tests/conftest.py`). CI equivalent: `python -m compileall .` and `python -m unittest discover tests`.
- Root-level `*_test.py` (e.g. `authorization_lifecycle_integrity_test.py`) are standalone async scripts — run directly with `python3 <file>.py`.
- Core API: `python3 main.py` → uvicorn on :3011 (`core/api.py`).
- Control CLI: `./a1ctl status` / `./a1ctl exec` — talks to `http://127.0.0.1:8000/v1`.
- education-os API: `cd products/education-os/api && python3 -m uvicorn app:app --host 127.0.0.1 --port 3012`.
- Node tooling (`package.json`: playwright, chrome-remote-interface, react-three): `npm install`.

## Runtime wiring (production topology)

Canonical launch: `education-os-launch.sh` (Termux home). One service per port — do not move these:

- **3011** — A1OS core engine (`python3 main.py`). Currently idle; edu owns 3012.
- **3012** — education-os API (`run-production.sh` → `uvicorn api.app:app --host 127.0.0.1 --port 3012 --workers 1 --proxy-headers`).
- **8080** — frontend + same-origin `/api` proxy (`education-os-web-server.py` serves `products/education-os/web`, proxies to 3012).
- **Cloudflare tunnel `a1os-prod`** (`~/.cloudflared/config.yml`) — `little-oaks.pyongcity.org/api/*` → 3012, everything else → 8080.
- **8000** — `a1ctl` gateway. Not currently running.

Watchdogs: `products/education-os/ops/watchdog.sh` (restarts API on 3012), `A1OS_RESTORED/ops/a1os-production-watchdog.sh` (core). Cron template: `~/crontab.txt` (install with `crontab crontab.txt`).

## Gotchas

- `.env` in repo root holds secrets (Cloudflare tokens, `SECRET_KEY`, `JWT_SECRET_KEY`). Never print or commit it.
- `products/education-os/deployments/little-oaks/data/education.db` is a tracked binary (`.gitignore` ignores `*.db`; this one was force-added) with local modifications. Release and acceptance pipelines depend on it — don't rebuild or drop it casually.
- `./little-oaks-release.sh` runs Stage 4–7 acceptance suites, backs up the DB, commits, tags, and **pushes to origin main**. Don't run casually.
- Stale paths: `run_all.sh` and `tests/run_test.py` reference `~/A1OS`, but the working copy is `~/A1OS_RESTORED`. Use the real path.
- Host memory is tight (~5.5Gi total, ~1.1Gi free) — avoid parallel heavy builds.
