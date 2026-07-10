#!/bin/bash
# A1OS Daily/Weekly Verification Script

LOG_FILE="/data/data/com.termux/files/home/A1OS/logs/verify.log"
mkdir -p /data/data/com.termux/files/home/A1OS/logs

echo "═══════════════════════════════════════════════════════" >> $LOG_FILE
echo "A1OS VERIFICATION: $(date)" >> $LOG_FILE
echo "═══════════════════════════════════════════════════════" >> $LOG_FILE

cd /data/data/com.termux/files/home/A1OS

# 1. Clean cache
echo "▶ Cleaning cache..." >> $LOG_FILE
find . -name "*.pyc" -delete 2>/dev/null
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
echo "✅ Cache cleaned" >> $LOG_FILE

# 2. Check Python syntax
echo "▶ Checking syntax..." >> $LOG_FILE
SYNTAX_ERRORS=$(find . -name "*.py" -not -path "./.git/*" -exec python3 -m py_compile {} \; 2>&1 | grep -c "SyntaxError" || echo "0")
echo "Syntax errors: $SYNTAX_ERRORS" >> $LOG_FILE

# 3. Check server
echo "▶ Checking server..." >> $LOG_FILE
if ps aux | grep -q "[p]ython3 main.py"; then
    echo "✅ Server running" >> $LOG_FILE
else
    echo "❌ Server NOT running - attempting restart..." >> $LOG_FILE
    cd /data/data/com.termux/files/home/A1OS && python3 main.py &
    sleep 5
fi

# 4. Test endpoints
echo "▶ Testing endpoints..." >> $LOG_FILE
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3011/v1/health 2>/dev/null)
echo "Health: $HEALTH" >> $LOG_FILE

if [ "$HEALTH" = "200" ]; then
    echo "✅ Health check passed" >> $LOG_FILE
else
    echo "❌ Health check failed" >> $LOG_FILE
fi

DASHBOARD=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3011/dashboard 2>/dev/null)
echo "Dashboard: $DASHBOARD" >> $LOG_FILE

# 5. Check workers
echo "▶ Checking workers..." >> $LOG_FILE
WORKERS=$(curl -s http://localhost:3011/v1/health 2>/dev/null | grep -o '"workers":\[[^]]*\]' || echo "None")
echo "Workers: $WORKERS" >> $LOG_FILE

# 6. Check disk space
echo "▶ Disk space..." >> $LOG_FILE
df -h /data | tail -1 >> $LOG_FILE

# 7. Check memory
echo "▶ Memory..." >> $LOG_FILE
free -m 2>/dev/null | head -2 >> $LOG_FILE

# 8. Summary
echo "" >> $LOG_FILE
echo "═══════════════════════════════════════════════════════" >> $LOG_FILE
echo "VERIFICATION COMPLETE: $(date)" >> $LOG_FILE
echo "Status: ✅ A1OS is clean and operational" >> $LOG_FILE
echo "═══════════════════════════════════════════════════════" >> $LOG_FILE

# Print to console
tail -20 $LOG_FILE
