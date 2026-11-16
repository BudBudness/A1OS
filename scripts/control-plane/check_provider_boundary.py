#!/usr/bin/env python3
"""Fail closed when excluded provider dependencies appear in control-plane source/config."""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from pathlib import Path

SCAN_DIRS = ("src", "config", "infra", "workflows")
TEXT_SUFFIXES = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".json", ".toml", ".yaml", ".yml", ".sh", ".env"}
DENIED = (
    ("Vercel", re.compile(r"vercel|VERCEL", re.IGNORECASE)),
    ("Supabase", re.compile(r"supabase|SUPABASE", re.IGNORECASE)),
    ("Convex", re.compile(r"convex|CONVEX", re.IGNORECASE)),
)


def inspect(root: Path) -> tuple[list[tuple[Path, int, str]], int]:
    violations: list[tuple[Path, int, str]] = []
    scanned = 0
    for directory in SCAN_DIRS:
        base = root / directory
        if not base.exists():
            continue
        for path in sorted(p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in TEXT_SUFFIXES):
            scanned += 1
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError, OSError) as exc:
                violations.append((path, 0, f"unreadable text/config file: {exc.__class__.__name__}"))
                continue
            for number, line in enumerate(lines, 1):
                for provider, pattern in DENIED:
                    if pattern.search(line):
                        violations.append((path, number, f"excluded provider reference: {provider}"))
    return violations, scanned


def self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "src").mkdir()
        (root / "src" / "clean.ts").write_text("export const runtime = 'cloudflare';\n", encoding="utf-8")
        found, scanned = inspect(root)
        assert scanned == 1 and not found, (scanned, found)
        (root / "src" / "blocked.ts").write_text("import { createClient } from '@supabase/supabase-js';\n", encoding="utf-8")
        found, scanned = inspect(root)
        assert scanned == 2 and any(item[2].endswith("Supabase") for item in found), found
    print("Provider boundary guard self-test: PASS")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("canonical-control-plane"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return 0

    violations, scanned = inspect(args.root)
    print(f"Scanned {scanned} control-plane source/config file(s).")
    if violations:
        for path, line, reason in violations:
            print(f"ERROR: {path}:{line}: {reason}")
        print("Provider boundary check: FAIL")
        return 1
    print("Provider boundary check: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
