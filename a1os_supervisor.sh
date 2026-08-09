#!/data/data/com.termux/files/usr/bin/bash
# RETIRED 2026-08-09 — replaced by the unified reconcile loop.
# Desired state:   ops/services.json
# Reconcile loop:  ops/a1os-reconciler.py  (driven hourly by the watchdog)
# Restart logic:   ops/adapters/
# This file is INERT. Do NOT start it — it was a pgrep-loop supervisor that
# raced the watchdog/launcher and caused the EADDRINUSE core outage.
exit 0
