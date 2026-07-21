#!/bin/bash

DB="a1os_state.db"
echo "--- 🛡️ A1OS SYSTEM HEALTH CHECK ---"

# 1. Integrity Check
echo "[1/3] Running DB Integrity..."
sqlite3 $DB "PRAGMA integrity_check;"

# 2. Record Verification
echo "[2/3] Verifying Data Registry..."
echo "Inventory Items: $(sqlite3 $DB 'SELECT count(*) FROM inventory_registry;')"
echo "CRM Profiles   : $(sqlite3 $DB 'SELECT count(*) FROM crm_profiles;')"
echo "Ledger Records : $(sqlite3 $DB 'SELECT count(*) FROM finance_ledger;')"

# 3. Process Initialization
echo "[3/3] Initializing Enterprise Workers..."
# Assuming your worker entry point is manager.py or a background daemon
nohup python3 ~/A1OS/manager.py > ~/A1OS/logs/worker.log 2>&1 &
echo "Workers active. Logs redirected to ~/A1OS/logs/worker.log."

echo "--- ✅ HEALTH CHECK COMPLETE ---"

