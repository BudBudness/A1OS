#!/usr/bin/env bash
# Run the repository and platform API test suites in isolated Python import contexts.
# The repository and platform API both contain an `api` package; running them in
# one pytest process can cache the wrong package during test collection.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
API_ROOT="$ROOT/platform/a1os-platform-api"

if ! command -v python >/dev/null 2>&1; then
  echo "ERROR: python is required." >&2
  exit 127
fi

echo "=== A1OS repository regression suite ==="
(
  cd "$ROOT" || exit 1
  PYTHONPATH="$ROOT" python -m pytest -q --ignore=platform/a1os-platform-api/tests
)
repo_status=$?

echo
echo "=== A1OS platform API suite ==="
(
  cd "$API_ROOT" || exit 1
  PYTHONPATH="$API_ROOT" python -m pytest -q tests
)
api_status=$?

echo
echo "=== Verification summary ==="
echo "Repository suite exit code: $repo_status"
echo "Platform API suite exit code: $api_status"

if [[ "$repo_status" -eq 0 && "$api_status" -eq 0 ]]; then
  echo "PASS: both suites passed."
  exit 0
fi

echo "FAIL: one or more test suites failed." >&2
exit 1
