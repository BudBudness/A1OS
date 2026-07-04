#!/bin/bash
while true; do
  # Write to temporary file first (atomic write)
  cat data/state.json > manifest.tmp
  tail -n 5 data/ingest/logs/audit.jsonl >> manifest.tmp
  # Atomically move temp to target (prevents partial reads)
  mv manifest.tmp manifest.json
  sleep 1
done
