from memory_intelligence.engine import MemoryEngine
import os, sqlite3, json, time, threading, subprocess
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
memory_engine = MemoryEngine()
CORS(app)

# ===== DATABASE =====
def init_db():
    with sqlite3.connect('data/a1os.db') as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS agents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, type TEXT, status TEXT,
                metadata TEXT, created TEXT, last_active TEXT
            );
            CREATE TABLE IF NOT EXISTS agent_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER, description TEXT,
                status TEXT, created TEXT
            );
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id INTEGER, log TEXT, created TEXT
            );
            CREATE TABLE IF NOT EXISTS workflows (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, steps TEXT, status TEXT,
                created TEXT, completed TEXT
            );
            CREATE TABLE IF NOT EXISTS knowledge (
                key TEXT PRIMARY KEY, value TEXT, updated TEXT
            );
        ''')
init_db()

# ===== AGENTS =====
agents = {}
agent_goals = {}
agent_logs = {}

def load_agents():
    global agents, agent_goals, agent_logs
    with sqlite3.connect('data/a1os.db') as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM agents").fetchall()
        agents = {r['id']: dict(r) for r in rows}
        agent_goals = {}
        agent_logs = {}
        for row in conn.execute("SELECT * FROM agent_goals"):
            agent_goals.setdefault(row['agent_id'], []).append(dict(row))
        for row in conn.execute("SELECT * FROM agent_logs"):
            agent_logs.setdefault(row['agent_id'], []).append(dict(row))

# ===== AUTONOMY =====
class AgentAutonomy:
    def __init__(self):
        self.running = True
        threading.Thread(target=self.run, daemon=True).start()
    def run(self):
        while self.running:
            try:
                with sqlite3.connect('data/a1os.db') as conn:
                    conn.row_factory = sqlite3.Row
                    rows = conn.execute("SELECT * FROM agents WHERE status = 'idle'").fetchall()
                    for agent in rows:
                        goal = f"Process {agent['name']} tasks"
                        conn.execute("INSERT INTO agent_goals (agent_id, description, status, created) VALUES (?, ?, ?, ?)",
                                     (agent['id'], goal, 'pending', datetime.now().isoformat()))
                        conn.execute("UPDATE agents SET status = 'working', last_active = ? WHERE id = ?",
                                     (datetime.now().isoformat(), agent['id']))
                        conn.execute("INSERT INTO agent_logs (agent_id, log, created) VALUES (?, ?, ?)",
                                     (agent['id'], f"Started: {goal}", datetime.now().isoformat()))
                        conn.commit()
                time.sleep(30)
            except Exception as e:
                print(f"Autonomy error: {e}")
                time.sleep(10)

# ===== WORKFLOW TRIGGERS =====
class WorkflowTriggers:
    def __init__(self):
        self.running = True
        threading.Thread(target=self.run, daemon=True).start()
    def run(self):
        while self.running:
            try:
                with sqlite3.connect('data/a1os.db') as conn:
                    conn.row_factory = sqlite3.Row
                    rows = conn.execute("SELECT * FROM workflows WHERE status = 'pending'").fetchall()
                    for wf in rows:
                        conn.execute("UPDATE workflows SET status = 'running' WHERE id = ?", (wf['id'],))
                        conn.commit()
                        # Simulate execution
                        time.sleep(2)
                        conn.execute("UPDATE workflows SET status = 'completed', completed = ? WHERE id = ?",
                                     (datetime.now().isoformat(), wf['id']))
                        conn.commit()
                time.sleep(60)
            except Exception as e:
                print(f"Workflow error: {e}")
                time.sleep(10)

# ===== API ROUTES =====
@app.route("/")
def root():
@app.route("/memory/stats")\ndef memory_stats():\n    stats = memory_engine.get_stats()\n    return jsonify({"total": stats.total, "working": stats.working, "episodic": stats.episodic, "long_term": stats.long_term, "vector": stats.vector, "graph_nodes": stats.graph_nodes, "graph_edges": stats.graph_edges, "avg_importance": stats.avg_importance})\n\n@app.route("/memory/search")\ndef memory_search():\n    q = request.args.get("q", "")\n    if not q:\n        return jsonify([])\n    results = memory_engine.search(q)\n    return jsonify(results)\n\n@app.route("/memory/retrieve", methods=["POST"])\ndef memory_retrieve():\n    data = request.json\n    if not data or "query" not in data:\n        return jsonify({"error": "Missing query"}), 400\n    results = memory_engine.retrieve(data["query"], data.get("top_k", 20))\n    return jsonify(results)\n\n@app.route("/memory/consolidate", methods=["POST"])\ndef memory_consolidate():\n    results = memory_engine.consolidate()\n    return jsonify(results)\n\n@app.route("/memory/graph")\ndef memory_graph():\n    relations = memory_engine.get_graph()\n    return jsonify({"relations": relations})\n\n@app.route("/memory/store", methods=["POST"])\ndef memory_store():\n    data = request.json\n    if not data or "content" not in data:\n        return jsonify({"error": "Missing content"}), 400\n    item = memory_engine.add(data["content"], data.get("type", "long_term"), data.get("metadata", {}))\n    return jsonify({"ok": True, "id": item.id})\n
    return jsonify({"status": "online", "version": "A1OS Hybrid v1.0", "modules": ["agents", "workflows", "knowledge"]})

@app.route("/agents", methods=["GET", "POST"])
def agents_route():
    if request.method == "POST":
        data = request.json
        if not data or "name" not in data:
            return jsonify({"error": "Missing name"}), 400
        with sqlite3.connect('data/a1os.db') as conn:
            cur = conn.execute(
                "INSERT INTO agents (name, type, status, metadata, created, last_active) VALUES (?, ?, ?, ?, ?, ?)",
                (data["name"], data.get("type", "worker"), "idle", "{}", datetime.now().isoformat(), datetime.now().isoformat())
            )
            conn.commit()
            load_agents()
            return jsonify({"id": cur.lastrowid, "ok": True})
    load_agents()
    return jsonify(list(agents.values()))

@app.route("/workflows", methods=["GET", "POST"])
def workflows_route():
    if request.method == "POST":
        data = request.json
        if not data or "name" not in data or "steps" not in data:
            return jsonify({"error": "Missing name or steps"}), 400
        with sqlite3.connect('data/a1os.db') as conn:
            cur = conn.execute(
                "INSERT INTO workflows (name, steps, status, created) VALUES (?, ?, ?, ?)",
                (data["name"], json.dumps(data["steps"]), "pending", datetime.now().isoformat())
            )
            conn.commit()
            return jsonify({"id": cur.lastrowid, "ok": True})
    with sqlite3.connect('data/a1os.db') as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM workflows").fetchall()
        return jsonify([dict(r) for r in rows])

@app.route("/knowledge", methods=["GET", "POST"])
def knowledge_route():
    if request.method == "POST":
        data = request.json
        if not data or "key" not in data or "value" not in data:
            return jsonify({"error": "Missing key or value"}), 400
        with sqlite3.connect('data/a1os.db') as conn:
            conn.execute("INSERT OR REPLACE INTO knowledge (key, value, updated) VALUES (?, ?, ?)",
                         (data["key"], data["value"], datetime.now().isoformat()))
            conn.commit()
            return jsonify({"ok": True})
    with sqlite3.connect('data/a1os.db') as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM knowledge").fetchall()
        return jsonify([dict(r) for r in rows])

@app.route("/system/status")
def system_status():
    load_agents()
    with sqlite3.connect('data/a1os.db') as conn:
        conn.row_factory = sqlite3.Row
        workflow_count = conn.execute("SELECT COUNT(*) FROM workflows").fetchone()[0]
        knowledge_count = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
    return jsonify({
        "status": "online",
        "agent_count": len(agents),
        "workflow_count": workflow_count,
        "knowledge_count": knowledge_count,
        "version": "A1OS Hybrid v1.0"
    })

# ===== START =====
if __name__ == "__main__":
    # Create default agents
    default_agents = ["Memory-Agent", "Knowledge-Agent", "Task-Agent", "Hardware-Agent",
                      "System-Agent", "Analytics-Agent", "Backup-Agent", "Communication-Agent"]
    for name in default_agents:
        with sqlite3.connect('data/a1os.db') as conn:
            conn.execute(
                "INSERT OR IGNORE INTO agents (name, type, status, metadata, created, last_active) VALUES (?, ?, ?, ?, ?, ?)",
                (name, "worker", "idle", "{}", datetime.now().isoformat(), datetime.now().isoformat())
            )
            conn.commit()
    load_agents()
    # Start background services
    AgentAutonomy()
    WorkflowTriggers()
    # Start server
    app.run(host="0.0.0.0", port=8086)

@app.route(/hardware/battery\, methods=[GET\])\ndef hardware_battery():\n    try:\n        result = subprocess.run([	ermux-battery-status\], capture_output=True, text=True, timeout=5)\n        if result.returncode != 0:\n            return jsonify({error\: Battery

    try:
        result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return jsonify({'error': 'Battery status failed'}), 500
        return jsonify({'ok': True, 'battery': json.loads(result.stdout)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/hardware/location', methods=['GET'])
    try:
        result = subprocess.run(['termux-location'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return jsonify({'error': 'Location failed'}), 500
        return jsonify({'ok': True, 'location': json.loads(result.stdout)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/hardware/battery', methods=['GET'])
    import subprocess, json
    try:
        result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return jsonify({'error': 'Battery failed'}), 500
        return jsonify({'ok': True, 'battery': json.loads(result.stdout)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/hardware/location', methods=['GET'])
    import subprocess, json
    try:
        result = subprocess.run(['termux-location'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return jsonify({'error': 'Location failed'}), 500
        return jsonify({'ok': True, 'location': json.loads(result.stdout)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
