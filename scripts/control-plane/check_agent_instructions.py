#!/usr/bin/env python3
"""Validate and print the applicable A1OS agent instruction chain.

This tool is intentionally deterministic. It does not assume that an agent
runtime automatically discovers AGENTS.md; agent launchers must invoke
--preflight before running work.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT_INSTRUCTIONS = "AGENTS.md"
CLAUDE_INSTRUCTIONS = "CLAUDE.md"
COPILOT_INSTRUCTIONS = ".github/copilot-instructions.md"
SCOPED_INSTRUCTIONS = {
    "canonical-control-plane": "canonical-control-plane/AGENTS.md",
}
REQUIRED_PHRASES = {
    ROOT_INSTRUCTIONS: (
        "GitHub + Cloudflare + Termux",
        "Never print or commit",
        "explicit approval",
    ),
    CLAUDE_INSTRUCTIONS: (
        "@AGENTS.md",
        "preflight",
        "approval policy",
    ),
    COPILOT_INSTRUCTIONS: (
        "AGENTS.md",
        "preflight",
        "GitHub + Cloudflare + Termux",
    ),
    "canonical-control-plane/AGENTS.md": (
        "GitHub",
        "Cloudflare",
        "Termux",
        "explicit approval",
        "release gates",
    ),
}
CONFLICT_PATTERNS = (
    re.compile(r"(?im)^\s*(?:approved platform|canonical platform)\s*:\s*.*\bVercel\b"),
    re.compile(r"(?im)^\s*(?:approved platform|canonical platform)\s*:\s*.*\bSupabase\b"),
    re.compile(r"(?im)^\s*use\s+Vercel\s+for\s+(?:hosting|deployment|runtime)"),
    re.compile(r"(?im)^\s*use\s+Supabase\s+for\s+(?:database|backend|runtime)"),
)


def applicable(root: Path, target: str) -> list[Path]:
    target_path = Path(target)
    chain = [root / ROOT_INSTRUCTIONS, root / CLAUDE_INSTRUCTIONS, root / COPILOT_INSTRUCTIONS]
    for scope, relative in SCOPED_INSTRUCTIONS.items():
        if target_path == Path(scope) or Path(scope) in target_path.parents:
            chain.append(root / relative)
    return chain


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    required = [ROOT_INSTRUCTIONS, CLAUDE_INSTRUCTIONS, COPILOT_INSTRUCTIONS, *SCOPED_INSTRUCTIONS.values()]
    for rel in required:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required instruction file: {rel}")
            continue
        content = path.read_text(encoding="utf-8")
        for phrase in REQUIRED_PHRASES.get(rel, ()):
            if phrase.casefold() not in content.casefold():
                errors.append(f"{rel}: required policy phrase missing: {phrase}")
        for pattern in CONFLICT_PATTERNS:
            match = pattern.search(content)
            if match:
                errors.append(f"{rel}: conflicting provider mandate: {match.group(0).strip()}")
    return errors


def preflight(root: Path, target: str, global_instructions: Path | None = None) -> int:
    # Preflight is an enforcement boundary, not merely an instruction printer.
    # Validate the complete governance set before declaring the loaded chain safe.
    errors = validate(root)
    if global_instructions is not None:
        errors.extend(validate_global(global_instructions))
    if errors:
        for error in errors:
            print(f"PRE-FLIGHT BLOCKED: {error}", file=sys.stderr)
        print("A1OS_AGENT_PREFLIGHT=FAIL", file=sys.stderr)
        return 1

    chain = applicable(root, target)
    missing = [path for path in chain if not path.is_file()]
    if missing:
        for path in missing:
            print(f"PRE-FLIGHT BLOCKED: missing {path.relative_to(root)}", file=sys.stderr)
        return 2
    print(f"A1OS_AGENT_PREFLIGHT target={target}")
    for path in chain:
        content = path.read_text(encoding="utf-8")
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        print(f"\n===== BEGIN {path.relative_to(root)} sha256={digest} =====")
        print(content.rstrip())
        print(f"===== END {path.relative_to(root)} =====")
    print("\nA1OS_AGENT_PREFLIGHT=PASS")
    return 0


def compare_working_copy(root: Path, copy: Path) -> list[str]:
    """Check shared governance without erasing worktree-specific operations.

    Root AGENTS.md may legitimately contain distinct runtime topology and
    environment details in separate worktrees. Enforce its governance
    invariants, but require byte-for-byte parity only for shared agent policy
    files that have no worktree-specific operational content.
    """
    errors: list[str] = []
    root_file = copy / ROOT_INSTRUCTIONS
    if not root_file.is_file():
        errors.append(f"{copy}: missing {ROOT_INSTRUCTIONS}")
    else:
        content = root_file.read_text(encoding="utf-8")
        for phrase in REQUIRED_PHRASES[ROOT_INSTRUCTIONS]:
            if phrase.casefold() not in content.casefold():
                errors.append(f"{copy}/{ROOT_INSTRUCTIONS}: required policy phrase missing: {phrase}")
        for pattern in CONFLICT_PATTERNS:
            match = pattern.search(content)
            if match:
                errors.append(
                    f"{copy}/{ROOT_INSTRUCTIONS}: conflicting provider mandate: "
                    f"{match.group(0).strip()}"
                )

    for rel in (CLAUDE_INSTRUCTIONS, COPILOT_INSTRUCTIONS, *SCOPED_INSTRUCTIONS.values()):
        expected = root / rel
        actual = copy / rel
        if not actual.is_file():
            errors.append(f"{copy}: missing {rel}")
            continue
        if hashlib.sha256(expected.read_bytes()).digest() != hashlib.sha256(actual.read_bytes()).digest():
            errors.append(f"{copy}: drift detected in {rel}")
    return errors


def validate_global(path: Path) -> list[str]:
    if not path.is_file():
        return [f"global instruction file not found: {path}"]
    content = path.read_text(encoding="utf-8")
    errors: list[str] = []
    for phrase in ("GitHub", "Cloudflare", "Termux", "explicit approval"):
        if phrase.casefold() not in content.casefold():
            errors.append(f"{path}: global mandate missing: {phrase}")
    for pattern in CONFLICT_PATTERNS:
        match = pattern.search(content)
        if match:
            errors.append(f"{path}: conflicting provider mandate: {match.group(0).strip()}")
    return errors


def self_test() -> None:
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / ".github").mkdir()
        (root / "canonical-control-plane").mkdir()
        (root / "AGENTS.md").write_text(
            "GitHub + Cloudflare + Termux. Never print or commit secrets. "
            "Require explicit approval.\n", encoding="utf-8"
        )
        (root / CLAUDE_INSTRUCTIONS).write_text(
            "@AGENTS.md\nRun preflight. Treat AGENTS.md as the approval policy.\n",
            encoding="utf-8"
        )
        (root / COPILOT_INSTRUCTIONS).write_text(
            "Read AGENTS.md and run preflight. GitHub + Cloudflare + Termux.\n",
            encoding="utf-8"
        )
        (root / SCOPED_INSTRUCTIONS["canonical-control-plane"]).write_text(
            "GitHub Cloudflare Termux. Obtain explicit approval. "
            "Follow release gates.\n", encoding="utf-8"
        )
        assert not validate(root), validate(root)
        assert preflight(root, "canonical-control-plane/src/main.py") == 0

        global_file = root / "global-instructions.md"
        global_file.write_text(
            "GitHub Cloudflare Termux. Require explicit approval.\\n",
            encoding="utf-8"
        )
        assert not validate_global(global_file)
        assert preflight(root, "canonical-control-plane/src/main.py", global_file) == 0
        global_file.write_text(
            "Use Vercel for hosting.\\n", encoding="utf-8"
        )
        assert any("conflicting provider mandate" in e for e in validate_global(global_file))
        assert preflight(root, "canonical-control-plane/src/main.py", global_file) == 1
        global_file.unlink()

        chain = applicable(root, "canonical-control-plane/src/main.py")
        assert [p.relative_to(root).as_posix() for p in chain] == [
            "AGENTS.md", "CLAUDE.md", ".github/copilot-instructions.md",
            "canonical-control-plane/AGENTS.md"
        ]
        (root / "canonical-control-plane/AGENTS.md").write_text(
            "Use Vercel for hosting.\n", encoding="utf-8"
        )
        assert any("conflicting provider mandate" in e for e in validate(root))
        # A conflicting policy must block preflight; printing the chain alone
        # must never produce a PASS receipt.
        assert preflight(root, "canonical-control-plane/src") == 1
        (root / "canonical-control-plane/AGENTS.md").write_text(
            "GitHub Cloudflare Termux. Obtain explicit approval. Follow release gates.\\n",
            encoding="utf-8"
        )
        copy = root / "worktree"
        copy.mkdir()
        for rel in (ROOT_INSTRUCTIONS, CLAUDE_INSTRUCTIONS, COPILOT_INSTRUCTIONS, *SCOPED_INSTRUCTIONS.values()):
            dest = copy / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes((root / rel).read_bytes())
        assert not compare_working_copy(root, copy)
        # Worktree-specific runtime documentation is allowed when shared
        # governance invariants remain present and non-conflicting.
        (copy / "AGENTS.md").write_text(
            "Local runtime topology differs. GitHub + Cloudflare + Termux. "
            "Never print or commit secrets. Require explicit approval.\\n",
            encoding="utf-8"
        )
        assert not compare_working_copy(root, copy)
        (copy / "AGENTS.md").write_text("Local runtime with no governance.\\n", encoding="utf-8")
        assert any("required policy phrase missing" in e for e in compare_working_copy(root, copy))
    print("Agent instruction integrity self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--for-path", default="canonical-control-plane/")
    parser.add_argument("--working-copy", action="append", default=[])
    parser.add_argument("--global-instructions", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    if args.self_test:
        self_test()
        return 0
    global_instructions = (
        args.global_instructions.expanduser().resolve()
        if args.global_instructions else None
    )
    if args.preflight:
        return preflight(root, args.for_path, global_instructions)
    errors = validate(root)
    for copy in args.working_copy:
        errors.extend(compare_working_copy(root, Path(copy).expanduser().resolve()))
    if global_instructions is not None:
        errors.extend(validate_global(global_instructions))
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Agent instruction integrity: FAIL")
        return 1
    print("Agent instruction integrity: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
