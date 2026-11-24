# A1OS Termux Environment Management

## Purpose

Provide a deterministic, auditable baseline for inspecting and maintaining the Android Termux operator environment. This is a local operator utility, not a background agent and not a package manager replacement.

## Current implementation

`scripts/termux-maintenance/a1os_termux_maintenance.py` provides:

- Read-only inventory of selected tool versions and executable paths.
- Git working-tree status for the known `A1OS` and `A1OS_RESTORED` worktrees.
- Approximate top-level home-directory sizes.
- Inventory of explicitly allowlisted reproducible cache directories.
- JSON output suitable for later health reporting and automation.
- Optional interactive cleanup limited to contents of the allowlisted caches.

It does not inspect file contents, environment variables beyond the Termux `PREFIX` path, Git remotes/configuration, credentials, tokens, SSH material, cloud configuration, database contents, or process command lines.

## Run

From the A1OS repository in Termux:

```sh
python3 scripts/termux-maintenance/a1os_termux_maintenance.py
python3 scripts/termux-maintenance/a1os_termux_maintenance.py --json
python3 scripts/termux-maintenance/a1os_termux_maintenance.py --output "$HOME/a1os-termux-inventory.json"
python3 scripts/termux-maintenance/a1os_termux_maintenance.py --self-test
```

The default command is read-only. JSON reports may contain local paths and worktree status; keep reports private and do not commit them.

## Guarded cache cleanup

```sh
python3 scripts/termux-maintenance/a1os_termux_maintenance.py --clean-safe-caches
```

The command prints the eligible cache paths and requires typing `CLEAN`. The allowlist is intentionally narrow:

- `$HOME/.cache/pip`
- `$HOME/.npm/_cacache`
- `$HOME/.cache/yarn`
- `$HOME/.cache/pypoetry`
- `$PREFIX/var/cache/apt/archives`

Only regular files below these exact cache roots are removed. Symlinks are not followed. The directories themselves remain. No package databases, installed packages, project directories, Git metadata, source files, databases, backups, secrets, credentials, runtime services, or configuration files are eligible.

This initial release does not automatically clean caches on a schedule. Do not add cron scheduling until the report format, allowlist and recovery/operational impact have been reviewed on the actual Termux host.

## Maintenance safety lifecycle

All future maintenance operations must follow:

`DISCOVER → CLASSIFY → VALIDATE → BACKUP → CLEAN → VERIFY → REPORT`

- Inventory first; do not infer that an unknown file is disposable.
- Classify by ownership and reproducibility.
- Validate exact paths and symlink boundaries.
- Back up user/project state before any operation that can affect it.
- Limit automatic cleanup to policy-approved reproducible caches and temporary artifacts.
- Verify filesystem and application health after changes.
- Emit an evidence report with actions, counts, skipped paths and failures.

## Explicitly out of scope

This release does not install, upgrade, downgrade or uninstall packages; kill processes; restart services; edit shell profiles; change permissions; modify cron; alter Git remotes or branches; move/rename project folders; rotate credentials; change Cloudflare resources; delete downloads or user files; or run repository-wide cleanup.

Those capabilities require separate scoped implementation, tests, backup/recovery evidence and the approval boundaries in the repository-root `AGENTS.md`.

## Verification status

The self-test uses temporary directories and synthetic files. Passing it validates the utility's local safety logic only. It does not establish that the utility has been executed on the user's Termux device or that the device's packages, worktrees or services are healthy.
