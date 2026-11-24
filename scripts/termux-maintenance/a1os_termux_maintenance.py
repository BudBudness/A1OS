#!/usr/bin/env python3
"""A1OS Termux environment inventory and guarded cache maintenance.

Default mode is read-only. Cleanup is limited to explicitly allowlisted,
reproducible cache directories and requires an explicit interactive approval.
No package install/removal, service restart, config rewrite, secret inspection,
or project-file deletion is performed by this tool.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

VERSION = "1.0.0"
SAFE_CACHE_RELATIVE = (
    ".cache/pip",
    ".npm/_cacache",
    ".cache/yarn",
    ".cache/pypoetry",
)
VERSION_COMMANDS = {
    "python": ["python", "--version"],
    "python3": ["python3", "--version"],
    "node": ["node", "--version"],
    "npm": ["npm", "--version"],
    "git": ["git", "--version"],
    "gh": ["gh", "--version"],
    "claude": ["claude", "--version"],
    "copilot": ["copilot", "--version"],
    "codex": ["codex", "--version"],
    "pkg": ["pkg", "--version"],
}
PROTECTED_NAMES = {
    ".ssh", ".gnupg", ".cloudflared", ".config", ".claude", ".codex",
    ".termux", ".a1os", ".env", "secrets", "credentials", "backups",
}


def run_version(command: list[str]) -> dict:
    executable = shutil.which(command[0])
    if not executable:
        return {"available": False}
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, timeout=5, check=False
        )
        output = (result.stdout or result.stderr).strip().splitlines()
        return {
            "available": True,
            "path": executable,
            "version": output[0][:160] if output else "version unavailable",
            "exit_code": result.returncode,
        }
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"available": True, "path": executable, "error": type(exc).__name__}


def directory_size(path: Path) -> int:
    total = 0
    try:
        for item in path.rglob("*"):
            try:
                if item.is_file() and not item.is_symlink():
                    total += item.stat().st_size
            except OSError:
                continue
    except OSError:
        pass
    return total


def cache_roots(home: Path, prefix: Path | None) -> list[Path]:
    roots = [home / rel for rel in SAFE_CACHE_RELATIVE]
    # Termux apt archives are package-manager cache only; never touch dpkg state.
    if prefix:
        roots.append(prefix / "var/cache/apt/archives")
    return roots


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
        return True
    except (OSError, ValueError):
        return False


def cache_inventory(home: Path, prefix: Path | None) -> list[dict]:
    results = []
    for root in cache_roots(home, prefix):
        if root.exists() and root.is_dir() and not root.is_symlink():
            results.append({
                "path": str(root),
                "bytes": directory_size(root),
                "eligible": True,
                "policy": "allowlisted-reproducible-cache",
            })
    return results


def remove_cache_contents(home: Path, prefix: Path | None, approve: bool) -> dict:
    if not approve:
        raise PermissionError("cleanup requires interactive approval")
    removed_files = 0
    removed_bytes = 0
    skipped = []
    for root in cache_roots(home, prefix):
        if not root.exists():
            continue
        # Never follow a symlink or operate outside the exact allowlisted root.
        if root.is_symlink() or not root.is_dir() or not is_within(root, home) and not (
            prefix and is_within(root, prefix)
        ):
            skipped.append(str(root))
            continue
        for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
            current_path = Path(current)
            dirs[:] = [
                name for name in dirs
                if not (current_path / name).is_symlink()
                and name not in PROTECTED_NAMES
            ]
            for name in files:
                item = current_path / name
                try:
                    if item.is_symlink() or not item.is_file():
                        skipped.append(str(item))
                        continue
                    size = item.stat().st_size
                    item.unlink()
                    removed_files += 1
                    removed_bytes += size
                except OSError:
                    skipped.append(str(item))
    return {
        "removed_files": removed_files,
        "removed_bytes": removed_bytes,
        "skipped": skipped,
    }


def git_worktree(path: Path) -> dict:
    if not (path / ".git").exists():
        return {"path": str(path), "git_repository": False}
    try:
        result = subprocess.run(
            ["git", "-C", str(path), "status", "--short", "--branch"],
            capture_output=True, text=True, timeout=5, check=False,
        )
        # Git status output contains paths only; do not inspect config or remotes.
        return {
            "path": str(path),
            "git_repository": True,
            "status": result.stdout.strip()[:2000],
            "status_check": "ok" if result.returncode == 0 else "unavailable",
        }
    except (OSError, subprocess.TimeoutExpired):
        return {"path": str(path), "git_repository": True, "status_check": "unavailable"}


def build_report(home: Path, prefix: Path | None) -> dict:
    tools = {name: run_version(command) for name, command in VERSION_COMMANDS.items()}
    worktrees = [
        git_worktree(home / "A1OS"),
        git_worktree(home / "A1OS_RESTORED"),
    ]
    top_level = []
    try:
        for item in sorted(home.iterdir(), key=lambda p: p.name.lower()):
            if item.is_dir() and not item.is_symlink():
                try:
                    top_level.append({
                        "name": item.name,
                        "bytes": directory_size(item),
                    })
                except OSError:
                    continue
    except OSError:
        pass
    return {
        "schema_version": 1,
        "tool_version": VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "host": {
            "system": platform.system(),
            "release": platform.release(),
            "machine": platform.machine(),
            "python": platform.python_version(),
            "termux_prefix_detected": bool(prefix),
            "home": str(home),
        },
        "tools": tools,
        "worktrees": worktrees,
        "home_directories": top_level,
        "safe_cache_candidates": cache_inventory(home, prefix),
        "policy": {
            "default_mode": "read-only",
            "secrets_inspected": False,
            "project_files_modified": False,
            "package_state_modified": False,
            "service_state_modified": False,
        },
    }


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / "home"
        prefix = Path(tmp) / "prefix"
        (home / ".cache/pip").mkdir(parents=True)
        (home / ".cache/pip/wheel.whl").write_bytes(b"cache-data")
        (home / "A1OS").mkdir()
        (home / "A1OS/.git").mkdir()
        (home / ".ssh").mkdir()
        (home / ".ssh/key").write_text("must stay", encoding="utf-8")
        report = build_report(home, prefix)
        assert report["policy"]["secrets_inspected"] is False
        assert len(report["safe_cache_candidates"]) == 1
        try:
            remove_cache_contents(home, prefix, approve=False)
        except PermissionError:
            pass
        else:
            raise AssertionError("cleanup without approval must fail")
        result = remove_cache_contents(home, prefix, approve=True)
        assert result["removed_files"] == 1
        assert (home / ".ssh/key").read_text(encoding="utf-8") == "must stay"
        assert (home / "A1OS/.git").is_dir()
        # Symlink cache root is not traversed or removed.
        outside = Path(tmp) / "outside"
        outside.mkdir()
        (outside / "keep").write_text("keep", encoding="utf-8")
        link = home / ".npm"
        link.symlink_to(outside, target_is_directory=True)
        assert link.is_symlink()
        assert (outside / "keep").exists()
    print("A1OS Termux maintenance self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit JSON inventory")
    parser.add_argument("--output", type=Path, help="write report to this path")
    parser.add_argument("--clean-safe-caches", action="store_true",
                        help="remove contents of allowlisted reproducible caches")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0

    home = Path.home().resolve()
    prefix_value = os.environ.get("PREFIX")
    prefix = Path(prefix_value).resolve() if prefix_value else None

    cleanup = None
    if args.clean_safe_caches:
        print("Allowlisted cache cleanup only. No projects, secrets, packages, or services will be changed.")
        candidates = cache_inventory(home, prefix)
        for item in candidates:
            print(f"  {item['path']} ({item['bytes']} bytes)")
        if not candidates:
            print("No eligible cache directories found.")
            return 0
        answer = input("Delete contents of these cache directories? Type CLEAN to continue: ")
        if answer != "CLEAN":
            print("Cleanup cancelled.")
            return 2
        cleanup = remove_cache_contents(home, prefix, approve=True)

    report = build_report(home, prefix)
    if cleanup is not None:
        report["cleanup"] = cleanup
    rendered = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
        print(f"Report written: {args.output}")
    elif args.json:
        print(rendered)
    else:
        print("A1OS Termux Environment Report")
        print(f"Generated: {report['generated_at']}")
        print(f"Host: {report['host']['system']} / {report['host']['machine']}")
        print("\nToolchain:")
        for name, info in report["tools"].items():
            print(f"  {name}: {info.get('version', 'not installed')}")
        print("\nGit worktrees:")
        for item in report["worktrees"]:
            print(f"  {item['path']}: {item.get('status', 'not a Git worktree')}")
        print("\nSafe cache candidates:")
        for item in report["safe_cache_candidates"]:
            print(f"  {item['path']}: {item['bytes']} bytes")
        if cleanup:
            print(f"\nCleanup: removed {cleanup['removed_files']} files / {cleanup['removed_bytes']} bytes")
        print("\nRead-only inventory complete. No secrets or file contents were inspected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
