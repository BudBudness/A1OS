#!/data/data/com.termux/files/usr/bin/python3
"""A1OS reconciler — diffs desired state (ops/services.json) against reality.

For each service in the registry (in boot order): probe the local health URL.
If it fails, run the service's adapter (restart script) and re-probe with
retries. Print one line per service on stdout so the watchdog can timestamp
and ntfy-alert them, and write a machine-readable summary to
state/reconciler-status.json.

External observer: if configured, fetch the Cloudflare health-checker
/status. A service that is externally "down" but locally healthy is reported
as a WARNING (not restarted) — a tunnel outage must not trigger a restart
loop.

Exit status: 0 if every service reconciled, 1 otherwise.

Adapters are spawned with close_fds so the watchdog flock (fd 9) is never
inherited by long-running children.
"""
import datetime
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

ROOT = os.path.expanduser("~/A1OS_RESTORED")
REGISTRY = os.path.join(ROOT, "ops/services.json")
STATUS_FILE = os.path.join(ROOT, "state/reconciler-status.json")
LOG_FILE = os.path.join(ROOT, "logs/reconciler.log")

PROBE_TIMEOUT = 5
ADAPTER_TIMEOUT = 120
MAX_RETRIES = 3


def log(msg: str) -> None:
    ts = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(LOG_FILE, "a") as fh:
        fh.write(f"{ts} {msg}\n")


def probe(url: str):
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT) as resp:
            return resp.status
    except Exception:
        return None


def run_adapter(service):
    adapter = service.get("adapter", [])
    
    if service.get("type") == "observer":
        return "observer-only"

    if not adapter:
        return "no-adapter"

    import subprocess

    try:
        subprocess.run(
            adapter,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return "adapter-ok"
    except subprocess.CalledProcessError:
        return "adapter-failed"


def external_status(observer_url: str) -> dict:
    if not observer_url:
        return {}
    try:
        req = urllib.request.Request(observer_url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=PROBE_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())
        return {svc["name"]: svc["status"] for svc in data.get("services", [])}
    except Exception as exc:
        log(f"external observer unavailable: {exc}")
        return {}


def main() -> int:
    os.makedirs(os.path.join(ROOT, "state"), exist_ok=True)
    os.makedirs(os.path.join(ROOT, "logs"), exist_ok=True)

    with open(REGISTRY) as fh:
        registry = json.load(fh)
    services = sorted(registry["services"], key=lambda s: s.get("boot_order", 999))
    external = external_status(registry.get("external_observer", ""))

    results = []
    failed = False
    for svc in services:
        name = svc["name"]

        # Observers never participate in lifecycle control
        if svc.get("type") == "observer":
            results.append({
                "name": name,
                "status": "observer"
            })
            print(f"PASS service={name} observer-only", flush=True)
            continue

        url = svc["health_local"]
        status = probe(url)

        if status is not None:
            entry = {
                "name": name,
                "status": "ok",
                "http": status
            }

            if external.get(name) == "down":
                entry["external"] = "down"
                print(
                    f"WARN service={name} external=down (local ok)",
                    flush=True
                )
            else:
                print(
                    f"PASS service={name}",
                    flush=True
                )

            results.append(entry)
            continue

        adapter_result = run_adapter(svc)

        recovered_status = None

        if adapter_result == "adapter-ok":
            for _ in range(MAX_RETRIES):
                recovered_status = probe(url)

                if recovered_status is not None:
                    break

                time.sleep(3)

        if recovered_status is not None:
            results.append({
                "name": name,
                "status": "recovered",
                "http": recovered_status
            })
            print(
                f"RECOVERED service={name} adapter=ok",
                flush=True
            )
        else:
            failed = True
            results.append({
                "name": name,
                "status": "down"
            })
            print(
                f"FAIL service={name} recovery-failed",
                flush=True
            )

    with open(STATUS_FILE, "w") as fh:
        json.dump(
            {
                "generated_at": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "overall": "down" if failed else "ok",
                "services": results,
            },
            fh,
            indent=2,
        )
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
