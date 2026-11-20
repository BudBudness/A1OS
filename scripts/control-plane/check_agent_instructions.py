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
    chain = [root / ROOT_INSTRUCTIONS]
    for scope, relative in SCOPED_INSTRUCTIONS.items():
        if target_path == Path(scope) or Path(scope) in target_path.parents:
            chain.append(root / relative)
    return chain


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    required = [ROOT_INSTRUCTIONS, COPILOT_INSTRUCTIONS, *SCOPED_INSTRUCTIONS.values()]
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


def preflight(root: Path, target: str) -> int:
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
        (root / COPILOT_INSTRUCTIONS).write_text(
            "Read AGENTS.md and run preflight. GitHub + Cloudflare + Termux.\n",
            encoding="utf-8"
        )
        (root / SCOPED_INSTRUCTIONS["canonical-control-plane"]).write_text(
            "GitHub Cloudflare Termux. Obtain explicit approval. "
            "Follow release gates.\n", encoding="utf-8"
        )
        assert not validate(root), validate(root)
        chain = applicable(root, "canonical-control-plane/src/main.py")
        assert [p.relative_to(root).as_posix() for p in chain] == [
            "AGENTS.md", "canonical-control-plane/AGENTS.md"
        ]
        (root / "canonical-control-plane/AGENTS.md").write_text(
            "Use Vercel for hosting.\n", encoding="utf-8"
        )
        assert any("conflicting provider mandate" in e for e in validate(root))
    print("Agent instruction integrity self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--preflight", action="store_true")
    parser.add_argument("--for-path", default="canonical-control-plane/")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.self_test:
        self_test()
        return 0
    if args.preflight:
        return preflight(root, args.for_path)
    errors = validate(root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("Agent instruction integrity: FAIL")
        return 1
    print("Agent instruction integrity: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
