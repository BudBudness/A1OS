#!/bin/bash
# Setup cron jobs for A1OS verification

# Create crontab file
cat > /data/data/com.termux/files/home/crontab.txt << 'CRON'
# A1OS Daily Clean and Verification - 1:00 AM every day
0 1 * * * /data/data/com.termux/files/home/A1OS/scripts/verify_and_clean.sh

# A1OS Weekly Clean and Verification - 12:00 PM every Sunday
0 12 * * 0 /data/data/com.termux/files/home/A1OS/scripts/verify_and_clean.sh

# A1OS Server Health Check - Every hour
0 * * * * curl -s http://localhost:3011/v1/health > /dev/null || (cd /data/data/com.termux/files/home/A1OS && python3 main.py &)
CRON

# Install crontab
crontab /data/data/com.termux/files/home/crontab.txt

echo "✅ Cron jobs installed!"
echo ""
echo "Scheduled jobs:"
echo "  📅 Daily at 1:00 AM - Clean and verify"
echo "  📅 Weekly on Sunday at 12:00 PM - Clean and verify"
echo "  📅 Every hour - Health check and auto-restart"
echo ""
echo "View crontab: crontab -l"
echo "View logs: tail -f ~/A1OS/logs/verify.log"
