#!/usr/bin/env python3
"""Scoped static provider-boundary policy; not a deployment-readiness check."""
from __future__ import annotations
import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

SCAN_DIRS = ("src", "config", "infra", "workflows")
SUFFIXES = {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx", ".json", ".toml", ".yaml", ".yml", ".sh", ".env", ".txt"}
RULES = (
    ("hosting/runtime", re.compile(r"""(?:@vercel/|vercel\.app\b|vercel\.com\b|vercel\s+(?:deploy|build)|VERCEL_[A-Z0-9_]*|uses:\s*[^#\s]*vercel)""", re.I)),
    ("database/backend", re.compile(r"""(?:@supabase/|supabase\.co\b|supabase\s+(?:functions|db)\s+|SUPABASE_[A-Z0-9_]*|supabase-js)""", re.I)),
    ("database/backend", re.compile(r"""(?:convex\.cloud\b|convex\.site\b|convex\s+deploy\b|CONVEX_[A-Z0-9_]*|convex/server|convex/react)""", re.I)),
    ("database/backend", re.compile(r"""(?:firebase-admin|firebase\.googleapis\.com|FIREBASE_[A-Z0-9_]*|firebase deploy)""", re.I)),
    ("identity/authentication", re.compile(r"""(?:auth0\.com\b|AUTH0_[A-Z0-9_]*|@auth0/|clerk\.(?:com|dev)\b|CLERK_[A-Z0-9_]*|@clerk/|okta\.com\b|OKTA_[A-Z0-9_]*|keycloak\b|KEYCLOAK_[A-Z0-9_]*|workos\.com\b|WORKOS_[A-Z0-9_]*)""", re.I)),
    ("identity/authentication", re.compile(r"""(?:accounts\.google\.com/o/oauth2|GOOGLE_OAUTH_[A-Z0-9_]*|google-auth-oauthlib)""", re.I)),
    ("CI/CD", re.compile(r"""(?:amondnet/vercel-action|supabase/setup-cli|vercel deploy|supabase functions deploy|convex deploy)""", re.I)),
)

@dataclass(frozen=True)
class Violation:
    path: Path
    line: int
    dependency_class: str

def _comment(line: str) -> bool:
    s=line.lstrip()
    return not s or s.startswith(("#", "//", "--"))

def inspect(root: Path) -> tuple[list[Violation], int]:
    found=[]; scanned=0
    for dirname in SCAN_DIRS:
        base=root/dirname
        if not base.exists(): continue
        if not base.is_dir():
            found.append(Violation(base,0,"workspace-integrity")); continue
        for path in sorted(p for p in base.rglob("*") if p.is_file() and p.suffix.lower() in SUFFIXES):
            # The provider policy is the rule inventory itself, not an application dependency.
            if path.relative_to(root).as_posix() == "config/provider-policy.json":
                continue
            scanned += 1
            try: lines=path.read_text(encoding="utf-8").splitlines()
            except (UnicodeDecodeError,OSError):
                found.append(Violation(path,0,"workspace-integrity")); continue
            for number,line in enumerate(lines,1):
                if _comment(line): continue
                for category,pattern in RULES:
                    if pattern.search(line): found.append(Violation(path,number,category))
    return found,scanned

def has_application_source(root: Path) -> bool:
    """Configuration alone is not an application implementation."""
    source = root / "src"
    if not source.is_dir():
        return False
    return any(
        path.is_file() and path.suffix.lower() in {".py", ".js", ".mjs", ".cjs", ".ts", ".tsx", ".jsx"}
        for path in source.rglob("*")
    )

def self_test() -> int:
    cases=(
        ("hosting","run: vercel deploy\n","hosting/runtime"),
        ("supabase","import '@supabase/supabase-js';\n","database/backend"),
        ("convex","import 'convex/server';\n","database/backend"),
        ("firebase","FIREBASE_PROJECT_ID=demo\n","database/backend"),
        ("auth0","AUTH0_DOMAIN=demo.auth0.com\n","identity/authentication"),
        ("clerk","import '@clerk/nextjs';\n","identity/authentication"),
        ("google-oauth","https://accounts.google.com/o/oauth2/auth\n","identity/authentication"),
        ("vercel-action","uses: amondnet/vercel-action@v2\n","hosting/runtime"),
        ("supabase-action","run: supabase functions deploy api\n","database/backend"),
    )
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp); (root/"src").mkdir()
        for name,content,expected in cases:
            p=root/"src"/(name+".ts"); p.write_text(content,encoding="utf-8")
            violations,_=inspect(root)
            assert any(v.dependency_class==expected for v in violations),(name,violations)
            p.unlink()
        (root/"src"/"approved.ts").write_text(
            "import 'cloudflare:workers';\nconst api='https://api.github.com';\n",encoding="utf-8")
        (root/"src"/"comments.ts").write_text(
            "// do not use Supabase or Vercel\n# not executable configuration\n",encoding="utf-8")
        violations,scanned=inspect(root)
        assert scanned==2 and not violations,(scanned,violations)
        empty=root/"empty"; empty.mkdir()
        violations,scanned=inspect(empty)
        assert scanned==0 and not violations,(scanned,violations)
    print(f"Provider boundary tests: PASS ({len(cases)} prohibited cases; approved providers; comments; empty workspace)")
    return 0

def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path("canonical-control-plane"))
    parser.add_argument("--self-test",action="store_true")
    parser.add_argument("--require-implementation",action="store_true")
    args=parser.parse_args()
    if args.self_test: return self_test()
    if not args.root.is_dir():
        print(f"Provider boundary: FAIL (workspace missing: {args.root})"); return 1
    violations,scanned=inspect(args.root)
    print(f"Scanned {scanned} control-plane source/config file(s).")
    if violations:
        for v in violations: print(f"ERROR: {v.path}:{v.line}: [{v.dependency_class}] prohibited dependency")
        print("Provider boundary: FAIL"); return 1
    if not has_application_source(args.root):
        print("Provider boundary: PASS; implementation status: NO_IMPLEMENTATION (configuration is not application source)")
        return 2 if args.require_implementation else 0
    print("Provider boundary: PASS; implementation status: APPLICATION_SOURCE_PRESENT (not deployment-ready)")
    return 0

if __name__=="__main__":
    sys.exit(main())
