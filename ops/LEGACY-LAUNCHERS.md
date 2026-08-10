# A1OS Legacy Launcher Authority Classification

These launchers are retained for compatibility/reference but are **not lifecycle
authorities**.

## Canonical authority

The production lifecycle authority is:

`ops/a1os-production-watchdog.sh`
→ `ops/a1os-reconciler.py`
→ `ops/services.json`
→ `ops/adapters/*.sh`

## Classified legacy launchers

### `a1os_supervisor.sh`
Legacy/manual compatibility launcher. Not invoked by the production cron.

### `ops/a1os_secondary_runtime.sh`
Legacy/manual secondary-runtime launcher. Not part of canonical reconciliation.

### `ops/a1os_failover_orchestrator.sh`
Legacy/manual failover orchestration. Not part of canonical reconciliation.

### `ops/supervisor/run.sh`
Legacy supervisor wrapper. Not part of canonical production lifecycle control.

### `education-os-launch.sh`
Manual convenience launcher. The production watchdog/reconciler owns
service restart authority.

### `products/education-os/web/server.py`
Tracked application server implementation used by the education-web adapter.
It is not itself an authority; `ops/adapters/restart-education-web.sh` is the
authority for starting it.

Do not delete these files solely because they are legacy. Remove them only
after all external/manual dependencies have been migrated.
