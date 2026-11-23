#!/usr/bin/env python3
"""Fail-closed GitHub Copilot hook for A1OS instruction integrity.

sessionStart injects the verified instruction chain. preToolUse revalidates the
entire governance set before every agent tool call. A passing hook returns no
permission decision, preserving Copilot's normal permission model.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

CHECKER = Path("scripts/control-plane/check_agent_instructions.py")


def find_repo_root(cwd: str | None) -> Path | None:
    candidates: list[Path] = []
    if cwd:
        candidates.append(Path(cwd).expanduser())
    else:
        workspace = os.environ.get("GITHUB_WORKSPACE")
        if workspace:
            candidates.append(Path(workspace).expanduser())
        candidates.append(Path.cwd())
    seen: set[Path] = set()
    for candidate in candidates:
        try:
            resolved = candidate.resolve()
        except OSError:
            continue
        for parent in (resolved, *resolved.parents):
            if parent in seen:
                continue
            seen.add(parent)
            if (parent / "AGENTS.md").is_file() and (parent / CHECKER).is_file():
                return parent
    return None


def run_preflight(root: Path, target: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / CHECKER), "--root", str(root),
         "--preflight", "--for-path", target],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=20,
        check=False,
    )


def run_guard(root: Path, event_name: str) -> dict[str, Any]:
    # Validate the full instruction set before every tool call. The checker
    # validates all required scoped files, not only the current target scope.
    if event_name in {"preToolUse", "PreToolUse"}:
        result = run_preflight(root, ".")
        if result.returncode != 0:
            reason = (result.stderr or result.stdout or "instruction validation failed").strip()
            return {
                "permissionDecision": "deny",
                "permissionDecisionReason": "A1OS instruction preflight failed: " + reason[:1200],
            }
        return {}

    if event_name in {"sessionStart", "SessionStart"}:
        root_result = run_preflight(root, ".")
        if root_result.returncode != 0:
            detail = (root_result.stderr or root_result.stdout or "instruction validation failed").strip()
            return {"additionalContext": "A1OS PREFLIGHT BLOCKED. Do not use tools. " + detail[:1200]}

        # Load the canonical-control-plane scope at session start as well.
        # Its constraints apply only to work within that directory.
        scoped_result = run_preflight(root, "canonical-control-plane/")
        if scoped_result.returncode != 0:
            detail = (scoped_result.stderr or scoped_result.stdout or "scoped preflight failed").strip()
            return {"additionalContext": "A1OS PREFLIGHT BLOCKED. Do not use tools. " + detail[:1200]}

        context = (
            "A1OS verified startup instruction chain. Apply repository-wide instructions to all work. "
            "Apply canonical-control-plane/AGENTS.md only to work under canonical-control-plane/.\n\n"
            + root_result.stdout.strip()
            + "\n\n"
            + scoped_result.stdout.strip()
        )
        return {"additionalContext": context}

    return {}


def handle_event(event: dict[str, Any]) -> dict[str, Any]:
    event_name = event.get("hook_event_name") or event.get("eventName") or ""
    cwd = event.get("cwd")
    root = find_repo_root(cwd if isinstance(cwd, str) else None)
    if root is None:
        if event_name in {"preToolUse", "PreToolUse"}:
            return {
                "permissionDecision": "deny",
                "permissionDecisionReason": "A1OS instruction guard could not locate the repository root; tool execution denied.",
            }
        if event_name in {"sessionStart", "SessionStart"}:
            return {"additionalContext": "A1OS PREFLIGHT BLOCKED: repository root not found. Do not use tools."}
        return {}
    return run_guard(root, event_name)


def self_test() -> None:
    hook_config = Path(__file__).with_name("a1os-instruction-guard.json")
    config = json.loads(hook_config.read_text(encoding="utf-8"))
    assert config.get("version") == 1
    configured_hooks = config.get("hooks", {})
    assert {"sessionStart", "preToolUse"}.issubset(configured_hooks)
    for event_name in ("sessionStart", "preToolUse"):
        entries = configured_hooks[event_name]
        assert entries and all(entry.get("type") == "command" for entry in entries)
        assert all("a1os_instruction_guard.py" in entry.get("bash", "") for entry in entries)

    source_checker = Path(__file__).resolve().parents[2] / CHECKER
    assert source_checker.is_file(), source_checker
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / ".github").mkdir()
        (root / "canonical-control-plane").mkdir()
        (root / "scripts/control-plane").mkdir(parents=True)
        shutil.copy2(source_checker, root / CHECKER)
        (root / "AGENTS.md").write_text(
            "GitHub + Cloudflare + Termux. Never print or commit secrets. Require explicit approval.\n",
            encoding="utf-8",
        )
        (root / ".github/copilot-instructions.md").write_text(
            "Read AGENTS.md and run preflight. GitHub + Cloudflare + Termux.\n",
            encoding="utf-8",
        )
        (root / "canonical-control-plane/AGENTS.md").write_text(
            "GitHub Cloudflare Termux. Obtain explicit approval. Follow release gates.\n",
            encoding="utf-8",
        )

        start = handle_event({"hook_event_name": "sessionStart", "cwd": str(root)})
        assert "A1OS_AGENT_PREFLIGHT=PASS" in start.get("additionalContext", "")
        assert "canonical-control-plane/AGENTS.md" in start.get("additionalContext", "")

        allowed = handle_event({"hook_event_name": "preToolUse", "cwd": str(root), "toolName": "bash"})
        assert allowed == {}, allowed

        (root / "canonical-control-plane/AGENTS.md").write_text(
            "Use Vercel for hosting.\n", encoding="utf-8"
        )
        denied = handle_event({"hook_event_name": "preToolUse", "cwd": str(root), "toolName": "bash"})
        assert denied.get("permissionDecision") == "deny", denied
        assert "conflicting provider mandate" in denied.get("permissionDecisionReason", "")

        missing_root = handle_event({"hook_event_name": "preToolUse", "cwd": "/tmp"})
        assert missing_root.get("permissionDecision") == "deny", missing_root

    print("A1OS Copilot instruction hook self-test: PASS")


def main() -> int:
    if "--self-test" in sys.argv[1:]:
        self_test()
        return 0
    try:
        event = json.load(sys.stdin)
        if not isinstance(event, dict):
            raise ValueError("hook input must be a JSON object")
        result = handle_event(event)
    except Exception as exc:  # Fail closed for preToolUse on malformed input/runtime errors.
        event_name = ""
        try:
            event_name = event.get("hook_event_name") or event.get("eventName") or ""
        except Exception:
            pass
        if event_name in {"preToolUse", "PreToolUse"}:
            result = {
                "permissionDecision": "deny",
                "permissionDecisionReason": f"A1OS instruction guard error; tool execution denied: {type(exc).__name__}: {exc}",
            }
        elif event_name in {"sessionStart", "SessionStart"}:
            result = {"additionalContext": f"A1OS PREFLIGHT BLOCKED: guard error {type(exc).__name__}: {exc}. Do not use tools."}
        else:
            result = {}
    print(json.dumps(result, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
