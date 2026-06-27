#!/bin/bash
echo "🔒 Hardening A1OS for production..."

# 1. Install production WSGI server
pip install gunicorn -q

# 2. Create systemd service (if available)
if command -v systemctl &>/dev/null; then
    cat > /tmp/a1os.service << 'SVC'
[Unit]
Description=A1OS Backend
After=network.target

[Service]
ExecStart=/data/data/com.termux/files/usr/bin/gunicorn -w 2 -b 127.0.0.1:8086 complete_system:app
Restart=always
User=u0_a433
WorkingDirectory=/data/data/com.termux/files/home/A1OS

[Install]
WantedBy=multi-user.target
SVC
    mv /tmp/a1os.service ~/.config/systemd/user/a1os.service
    systemctl --user daemon-reload
    systemctl --user enable a1os.service
    systemctl --user start a1os.service
    echo "✅ Systemd service installed"
else
    echo "⚠️ systemctl not available (Termux). Using screen."
fi

# 3. Create backup script
cat > scripts/backup.sh << 'BACKUP'
#!/bin/bash
cd "$(dirname "$0")/.."
mkdir -p backups
cp data/a1os.db backups/a1os_$(date +%Y%m%d_%H%M%S).db
find backups -name "*.db" -mtime +7 -delete
echo "✅ Backup completed"
BACKUP
chmod +x scripts/backup.sh

# 4. Add cron job for backups
(crontab -l 2>/dev/null; echo "0 2 * * * $HOME/A1OS/scripts/backup.sh") | crontab -

echo "✅ Production hardening complete"
