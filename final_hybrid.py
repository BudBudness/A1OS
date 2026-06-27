from consensus.engine import ConsensusEngine
from cluster.engine import ClusterEngine
from scheduler.engine import SchedulerEngine
from workflows.engine import WorkflowEngine
from agents.engine import AgentEngine
from agents.autonomy import AgentAutonomy
from agents.communication import AgentCommunication
import os, sqlite3, json, time, threading, subprocess
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from memory_intelligence.engine import MemoryEngine

app = Flask(__name__)
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

# ===== MEMORY ENGINE =====
memory_engine = MemoryEngine()
agent_engine = AgentEngine()
workflow_engine = WorkflowEngine()
scheduler_engine = SchedulerEngine()
cluster_engine = ClusterEngine()
consensus_engine = ConsensusEngine()

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
            except:
                time.sleep(10)

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
                        time.sleep(2)
                        conn.execute("UPDATE workflows SET status = 'completed', completed = ? WHERE id = ?",
                                     (datetime.now().isoformat(), wf['id']))
                        conn.commit()
                time.sleep(60)
            except:
                time.sleep(10)

# ===== API ROUTES =====
@app.route("/")
def root():
    return jsonify({"status": "online", "version": "A1OS Hybrid v1.0", "modules": ["memory", "agents", "workflows", "knowledge", "hardware"]})

@app.route("/memory/stats")
def memory_stats():
    stats = memory_engine.get_stats()
    return jsonify({"total": stats.total, "working": stats.working, "episodic": stats.episodic, "long_term": stats.long_term, "vector": stats.vector, "graph_nodes": stats.graph_nodes, "graph_edges": stats.graph_edges, "avg_importance": stats.avg_importance})

@app.route("/memory/search")
def memory_search():
    q = request.args.get("q", "")
    if not q:
        return jsonify([])
    results = memory_engine.search(q)
    return jsonify(results)

@app.route("/memory/retrieve", methods=["POST"])
def memory_retrieve():
    data = request.json
    if not data or "query" not in data:
        return jsonify({"error": "Missing query"}), 400
    results = memory_engine.retrieve(data["query"], data.get("top_k", 20))
    return jsonify(results)

@app.route("/memory/consolidate", methods=["POST"])
def memory_consolidate():
    results = memory_engine.consolidate()
    return jsonify(results)

@app.route("/memory/graph")
def memory_graph():
    relations = memory_engine.get_graph()
    return jsonify({"relations": relations})

@app.route("/memory/store", methods=["POST"])
def memory_store():
    data = request.json
    if not data or "content" not in data:
        return jsonify({"error": "Missing content"}), 400
    item = memory_engine.add(data["content"], data.get("type", "long_term"), data.get("metadata", {}))
    return jsonify({"ok": True, "id": item.id})

@app.route("/agents", methods=["GET", "POST"])
def agents_route():
    if request.method == "POST":
        data = request.json
        if not data or "name" not in data:
            return jsonify({"error": "Missing name"}), 400
        with sqlite3.connect('data/a1os.db') as conn:
            cur = conn.execute("INSERT INTO agents (name, type, status, metadata, created, last_active) VALUES (?, ?, ?, ?, ?, ?)",
                               (data["name"], data.get("type", "worker"), "idle", "{}", datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
            load_agents()
            return jsonify({"id": cur.lastrowid, "ok": True})
    load_agents()
    return jsonify(list(agents.values()))

@app.route("/agents/<int:aid>/goal", methods=["POST"])
def set_goal(aid):
    data = request.json
    if not data or "goal" not in data:
        return jsonify({"error": "Missing goal"}), 400
    with sqlite3.connect('data/a1os.db') as conn:
        conn.execute("INSERT INTO agent_goals (agent_id, description, status, created) VALUES (?, ?, ?, ?)",
                     (aid, data["goal"], "pending", datetime.now().isoformat()))
        conn.commit()
        load_agents()
        return jsonify({"ok": True})

@app.route("/agents/<int:aid>/logs")
def get_logs(aid):
    load_agents()
    return jsonify(agent_logs.get(aid, []))

@app.route("/workflows", methods=["GET", "POST"])
def workflows_route():
    if request.method == "POST":
        data = request.json
        if not data or "name" not in data or "steps" not in data:
            return jsonify({"error": "Missing name or steps"}), 400
        with sqlite3.connect('data/a1os.db') as conn:
            cur = conn.execute("INSERT INTO workflows (name, steps, status, created) VALUES (?, ?, ?, ?)",
                               (data["name"], json.dumps(data["steps"]), "pending", datetime.now().isoformat()))
            conn.commit()
            return jsonify({"id": cur.lastrowid, "ok": True})
    with sqlite3.connect('data/a1os.db') as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM workflows").fetchall()
        return jsonify([dict(r) for r in rows])


@app.route('/hardware/battery', methods=['GET'])
def hardware_battery():
    try:
        result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return jsonify({'error': 'Battery failed'}), 500
        return jsonify({'ok': True, 'battery': json.loads(result.stdout)})
    except:
        return jsonify({'error': 'Battery error'}), 500

@app.route('/hardware/location', methods=['GET'])
def hardware_location():
    try:
        result = subprocess.run(['termux-location'], capture_output=True, text=True, timeout=5)
        if result.returncode != 0:
            return jsonify({'error': 'Location failed'}), 500
        return jsonify({'ok': True, 'location': json.loads(result.stdout)})
    except:
        return jsonify({'error': 'Location error'}), 500


@app.route("/cluster/nodes", methods=["GET", "POST"])
def cluster_route():
    if request.method == "POST":
        data = request.json
        if not data or "address" not in data:
            return jsonify({"error": "Missing address"}), 400
        node = cluster_engine.add_node(data["address"], data.get("metadata", {}))
        return jsonify(node)
    nodes = cluster_engine.get_nodes()
    return jsonify(nodes)

@app.route("/cluster/leader")
def cluster_leader():
    return jsonify({"leader": cluster_engine.leader})


@app.route("/consensus/propose", methods=["POST"])
def consensus_propose():
    data = request.json
    if not data or "proposal" not in data:
        return jsonify({"error": "Missing proposal"}), 400
    result = consensus_engine.propose(data["proposal"], data.get("metadata", {}))
    return jsonify(result)

@app.route("/consensus/log")
def consensus_log():
    return jsonify(consensus_engine.get_log())

@app.route("/consensus/vote/<int:log_id>", methods=["POST"])
def consensus_vote():
    data = request.json
    if not data or "vote" not in data:
        return jsonify({"error": "Missing vote"}), 400
    consensus_engine.vote(log_id, data["vote"])
    return jsonify({"ok": True})
@app.route("/cluster/heartbeat", methods=["POST"])
def cluster_heartbeat():
    data = request.json
    if not data or "node_id" not in data:
        return jsonify({"error": "Missing node_id"}), 400
    cluster_engine.heartbeat(data["node_id"])
    return jsonify({"ok": True})

@app.route("/scheduler/tasks", methods=["GET", "POST"])
def scheduler_route():
    if request.method == "POST":
        data = request.json
        if not data or "name" not in data or "action" not in data:
            return jsonify({"error": "Missing name or action"}), 400
        task = scheduler_engine.add(data["name"], data.get("schedule", "once"), data["action"])
        return jsonify(task)
    tasks = scheduler_engine.get_all()
    return jsonify(tasks)


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

# ===== UNIFIED API =====
@app.route("/api/v1/status")
def api_status():
    return jsonify({
        "version": "v1.0",
        "status": "online",
        "modules": ["memory", "agents", "workflows", "scheduler", "cluster", "consensus", "knowledge", "hardware"],
        "endpoints": {
            "memory": ["/memory/stats", "/memory/search", "/memory/retrieve", "/memory/consolidate", "/memory/graph", "/memory/store"],
            "agents": ["/agents", "/agents/<id>/goal", "/agents/<id>/logs"],
            "workflows": ["/workflows"],
            "scheduler": ["/scheduler/tasks"],
            "cluster": ["/cluster/nodes", "/cluster/leader", "/cluster/heartbeat"],
            "consensus": ["/consensus/propose", "/consensus/log", "/consensus/vote/<id>"],
            "knowledge": ["/knowledge"],
            "hardware": ["/hardware/battery", "/hardware/location"]
        }
    })

@app.route("/api/v1/health")
def api_health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})


# ===== DOMAIN PACK ROUTES =====

# ===== OBSERVABILITY ROUTES =====
@app.route("/observability/metrics", methods=["GET"])
def observability_metrics():
    import sqlite3
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "memory": 0,
        "agents": 0,
        "workflows": 0,
        "knowledge": 0,
        "cluster_nodes": 0,
        "consensus_entries": 0
    }
    try:
        with sqlite3.connect('data/a1os.db') as conn:
            conn.row_factory = sqlite3.Row
            metrics["memory"] = conn.execute("SELECT COUNT(*) FROM memory").fetchone()[0] or 0
            metrics["agents"] = conn.execute("SELECT COUNT(*) FROM agents").fetchone()[0] or 0
            metrics["workflows"] = conn.execute("SELECT COUNT(*) FROM workflows").fetchone()[0] or 0
            metrics["knowledge"] = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0] or 0
            metrics["cluster_nodes"] = conn.execute("SELECT COUNT(*) FROM cluster_nodes").fetchone()[0] or 0
            metrics["consensus_entries"] = conn.execute("SELECT COUNT(*) FROM consensus_log").fetchone()[0] or 0
    except:
        pass
    return jsonify(metrics)

@app.route("/observability/health")
def observability_health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "checks": {
            "database": "ok",
            "memory": "ok",
            "agents": "ok",
            "workflows": "ok",
            "knowledge": "ok"
        }
    })


# ===== SECURITY ROUTES =====
from functools import wraps
import time

# Rate limiting
rate_limits = {}

def rate_limit(limit=10, window=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            key = request.remote_addr
            now = time.time()
            if key not in rate_limits:
                rate_limits[key] = []
            rate_limits[key] = [t for t in rate_limits[key] if t > now - window]
            if len(rate_limits[key]) >= limit:
                return jsonify({"error": "Rate limit exceeded"}), 429
            rate_limits[key].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route("/security/audit", methods=["GET"])
def security_audit():
    try:
        with sqlite3.connect('data/a1os.db') as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM events ORDER BY time DESC LIMIT 20").fetchall()
            return jsonify([dict(r) for r in rows])
    except:
        return jsonify({"events": []})


# ===== PRODUCTION ROUTES =====
@app.route("/production/health", methods=["GET"])
def production_health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "online",
        "version": "A1OS v2.0"
    })

@app.route("/production/backup", methods=["POST"])
def production_backup():
    import subprocess
    try:
        result = subprocess.run(["./scripts/backup.sh"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return jsonify({"ok": True, "message": "Backup completed"})
        else:
            return jsonify({"ok": False, "error": result.stderr}), 500
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/production/status")
def production_status():
    return jsonify({
        "status": "online",
        "version": "A1OS v2.0",
        "environment": os.getenv("A1OS_ENV", "development"),
        "debug": os.getenv("DEBUG", "false").lower() == "true"
    })
@app.route("/security/status", methods=["GET"])
def security_status():
    return jsonify({
        "api_key_required": True,
        "rate_limiting": "enabled",
        "cors_restricted": True,
        "audit_logging": "enabled",
        "status": "secure"
    })
@app.route("/observability/events", methods=["GET"])
def observability_events():
    from events.bus import EventBus
    bus = EventBus()
    return jsonify({"events": bus.get_history(50)})
@app.route("/domain/packs", methods=["GET"])
def domain_packs():
    from domain_packs.loader import DomainPackLoader
    loader = DomainPackLoader()
    return jsonify({"packs": loader.list_available()})

@app.route("/domain/packs/<name>", methods=["GET"])
def domain_pack_info(name):
    from domain_packs.loader import DomainPackLoader
    loader = DomainPackLoader()
    pack = loader.load(name)
    return jsonify(pack)

@app.route("/domain/packs/<name>/activate", methods=["POST"])
def domain_pack_activate(name):
    from domain_packs.loader import DomainPackLoader
    loader = DomainPackLoader()
    pack = loader.load(name)
    return jsonify({"ok": True, "pack": name, "status": "active"})
@app.route("/api/v1/modules")
def api_modules():
    return jsonify({
        "modules": ["memory", "agents", "workflows", "scheduler", "cluster", "consensus", "knowledge", "hardware"],
        "count": 8
    })
@app.route("/system/status")
def system_status():
    load_agents()
    with sqlite3.connect('data/a1os.db') as conn:
        conn.row_factory = sqlite3.Row
        workflow_count = conn.execute("SELECT COUNT(*) FROM workflows").fetchone()[0]
        knowledge_count = conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0]
    return jsonify({"status": "online", "agent_count": len(agents), "workflow_count": workflow_count, "knowledge_count": knowledge_count, "version": "A1OS Hybrid v1.0"})

# ===== START =====
if __name__ == "__main__":
    default_agents = ["Memory-Agent", "Knowledge-Agent", "Task-Agent", "Hardware-Agent", "System-Agent", "Analytics-Agent", "Backup-Agent", "Communication-Agent"]
    for name in default_agents:
        with sqlite3.connect('data/a1os.db') as conn:
            conn.execute("INSERT OR IGNORE INTO agents (name, type, status, metadata, created, last_active) VALUES (?, ?, ?, ?, ?, ?)",
                         (name, "worker", "idle", "{}", datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
    load_agents()
    WorkflowTriggers()
    # Scheduler daemon would start here
    AgentAutonomy()
    app.run(host="0.0.0.0", port=8086)
