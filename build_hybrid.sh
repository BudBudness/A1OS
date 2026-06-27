#!/bin/bash
echo "🚀 A1OS Hybrid Platform Build"
echo "================================"

# Command 1: Core Stabilization
echo "[1/7] Stabilizing core..."
pkill -f gunicorn 2>/dev/null
pkill -f http.server 2>/dev/null
screen -wipe 2>/dev/null
rm -f data/a1os.db
python3 -c "from complete_system import init_db; init_db();" 2>/dev/null
sqlite3 data/a1os.db "UPDATE agents SET metadata = '{}';" 2>/dev/null
sqlite3 data/a1os.db "UPDATE knowledge SET metadata = '{}';" 2>/dev/null
sqlite3 data/a1os.db "UPDATE scheduled_tasks SET metadata = '{}';" 2>/dev/null
sed -i '/register_hardware_routes(app)/d' complete_system.py 2>/dev/null
sed -i '/register_domain_routes(app)/a register_hardware_routes(app)' complete_system.py 2>/dev/null
screen -dmS backend gunicorn -w 2 -b 127.0.0.1:8086 complete_system:app
sleep 3
cd ui/pwa && screen -dmS pwa python3 -m http.server 8000
cd ~/A1OS
echo "✅ Core stabilized"

# Command 2: Agent Ecosystem
echo "[2/7] Creating 8 agents..."
for agent in "Memory-Agent" "Knowledge-Agent" "Task-Agent" "Hardware-Agent" "System-Agent" "Analytics-Agent" "Backup-Agent" "Communication-Agent"; do
  curl -s -X POST http://localhost:8086/agents -H "X-API-Key: f8baeb69ea9311098aaa8992ada6ab1c6aeb42cfdcef3391c5f5d9ed353b2108" -H "Content-Type: application/json" -d "{\"name\":\"$agent\",\"type\":\"worker\"}" > /dev/null
done
echo "✅ 8 agents created"

# Command 3: Workflow Engine
echo "[3/7] Creating workflows..."
curl -s -X POST http://localhost:8086/workflows -H "X-API-Key: f8baeb69ea9311098aaa8992ada6ab1c6aeb42cfdcef3391c5f5d9ed353b2108" -H "Content-Type: application/json" -d '{"name":"Daily Backup","steps":[{"agent":"Backup-Agent","action":"backup_memory"}]}' > /dev/null
curl -s -X POST http://localhost:8086/workflows -H "X-API-Key: f8baeb69ea9311098aaa8992ada6ab1c6aeb42cfdcef3391c5f5d9ed353b2108" -H "Content-Type: application/json" -d '{"name":"Hardware Monitor","steps":[{"agent":"Hardware-Agent","action":"check_battery"},{"agent":"Hardware-Agent","action":"check_location"}]}' > /dev/null
curl -s -X POST http://localhost:8086/workflows -H "X-API-Key: f8baeb69ea9311098aaa8992ada6ab1c6aeb42cfdcef3391c5f5d9ed353b2108" -H "Content-Type: application/json" -d '{"name":"Knowledge Sync","steps":[{"agent":"Knowledge-Agent","action":"sync_data"}]}' > /dev/null
echo "✅ Workflows created"

# Command 4: Data Feeds
echo "[4/7] Starting data feeds..."
cat > scripts/data_feeds.sh << 'FEED'
#!/bin/bash
while true; do
  curl -s http://localhost:8086/hardware/battery > /dev/null 2>&1
  curl -s http://localhost:8086/hardware/location > /dev/null 2>&1
  sleep 60
done
FEED
chmod +x scripts/data_feeds.sh
nohup ./scripts/data_feeds.sh > /dev/null 2>&1 &
echo "✅ Data feeds running"

# Command 5: Corporation Dashboard
echo "[5/7] Updating dashboard..."
cd ui/pwa
sed -i '/<div id="messages">/a <div id="corp-dashboard" style="display:none;padding:16px;background:#1a1a2e;border-radius:12px;margin-bottom:16px;"><h3>🏢 Corporation Status</h3><div id="agent-status-list"></div><div id="workflow-status-list"></div></div>' index.html
sed -i '/function addMsg/a function showCorpDashboard(){const dashboard=document.getElementById("corp-dashboard");dashboard.style.display="block";fetch("/agents").then(r=>r.json()).then(data=>{document.getElementById("agent-status-list").innerHTML=data.map(a=>`<div>${a.name}: ${a.status}</div>`).join("")});fetch("/workflows").then(r=>r.json()).then(data=>{document.getElementById("workflow-status-list").innerHTML=data.map(w=>`<div>${w.name}: ${w.status}</div>`).join("")})}' index.html
cd ~/A1OS
echo "✅ Dashboard updated"

# Command 6: East Africa Localization
echo "[6/7] Localizing for East Africa..."
sqlite3 data/a1os.db "INSERT OR REPLACE INTO knowledge (key, value, updated) VALUES ('currency', 'UGX', datetime('now'));"
sqlite3 data/a1os.db "INSERT OR REPLACE INTO knowledge (key, value, updated) VALUES ('region', 'East Africa', datetime('now'));"
sqlite3 data/a1os.db "INSERT OR REPLACE INTO knowledge (key, value, updated) VALUES ('languages', 'English, Swahili, Luganda', datetime('now'));"
echo "✅ Localized for East Africa"

# Command 7: Platform Ready
echo "[7/7] Platform ready..."
echo "✅ A1OS Hybrid Platform Ready"
curl -s http://localhost:8086/system/status -H "X-API-Key: f8baeb69ea9311098aaa8992ada6ab1c6aeb42cfdcef3391c5f5d9ed353b2108" | python3 -m json.tool
termux-open http://localhost:8000
echo "================================"
echo "🌍 A1OS is now a hybrid platform."
echo "🎯 You control strategy. Agents execute tactics."
