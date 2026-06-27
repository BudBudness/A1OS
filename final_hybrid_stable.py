import os, sqlite3, json, time, threading, subprocess
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from functools import wraps

app = Flask(__name__)
CORS(app)

def init_db():
    with sqlite3.connect('data/a1os.db') as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, content TEXT, type TEXT, metadata TEXT, created TEXT);
            CREATE TABLE IF NOT EXISTS agents (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, type TEXT, status TEXT, metadata TEXT, created TEXT, last_active TEXT);
            CREATE TABLE IF NOT EXISTS agent_goals (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id INTEGER, description TEXT, status TEXT, created TEXT);
            CREATE TABLE IF NOT EXISTS agent_logs (id INTEGER PRIMARY KEY AUTOINCREMENT, agent_id INTEGER, log TEXT, created TEXT);
            CREATE TABLE IF NOT EXISTS workflows (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, steps TEXT, status TEXT, created TEXT, completed TEXT);
            CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, schedule TEXT, action TEXT, status TEXT, created TEXT, last_run TEXT);
            CREATE TABLE IF NOT EXISTS cluster_nodes (id INTEGER PRIMARY KEY AUTOINCREMENT, address TEXT, status TEXT, metadata TEXT, joined TEXT, last_heartbeat TEXT);
            CREATE TABLE IF NOT EXISTS consensus_log (id INTEGER PRIMARY KEY AUTOINCREMENT, term INTEGER, proposal TEXT, status TEXT, metadata TEXT, timestamp TEXT);
            CREATE TABLE IF NOT EXISTS knowledge (key TEXT PRIMARY KEY, value TEXT, metadata TEXT, updated TEXT);
            CREATE TABLE IF NOT EXISTS events (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, data TEXT, time TEXT);
            CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, api_key TEXT, created TEXT);
        ''')
init_db()

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key:
            return jsonify({'error': 'Missing API key'}), 401
        with sqlite3.connect('data/a1os.db') as conn:
            user = conn.execute('SELECT * FROM users WHERE api_key = ?', (api_key,)).fetchone()
            if not user:
                return jsonify({'error': 'Invalid API key'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route("/")
def root():
    return jsonify({"status": "online", "version": "A1OS v2.0", "modules": ["memory", "agents", "cluster", "consensus", "scheduler", "knowledge", "events", "system"]})

@app.route("/memory/stats", methods=['GET'])
@require_auth
def memory_stats():
    with sqlite3.connect('data/a1os.db') as conn:
        total = conn.execute('SELECT COUNT(*) FROM memory').fetchone()[0] or 0
        long_term = conn.execute("SELECT COUNT(*) FROM memory WHERE type='long_term'").fetchone()[0] or 0
        working = conn.execute("SELECT COUNT(*) FROM memory WHERE type='working'").fetchone()[0] or 0
        return jsonify({"total": total, "long_term": long_term, "working": working, "episodic": 0, "vector": 0})

@app.route("/memory/store", methods=['POST'])
@require_auth
def memory_store():
    data = request.json
    if not data or 'content' not in data:
        return jsonify({'error': 'Missing content'}), 400
    import hashlib
    doc_id = hashlib.md5(data['content'].encode()).hexdigest()
    with sqlite3.connect('data/a1os.db') as conn:
        conn.execute("INSERT OR REPLACE INTO memory (id, content, type, metadata, created) VALUES (?, ?, ?, ?, ?)",
                     (doc_id, data['content'], data.get('type', 'long_term'), json.dumps(data.get('metadata', {})), datetime.now().isoformat()))
        conn.commit()
    return jsonify({"ok": True, "id": doc_id})

@app.route("/memory/search", methods=['GET'])
@require_auth
def memory_search():
    q = request.args.get('q', '')
    with sqlite3.connect('data/a1os.db') as conn:
        rows = conn.execute("SELECT * FROM memory WHERE content LIKE ?", (f'%{q}%',)).fetchall()
        return jsonify([{"id": r[0], "content": r[1], "type": r[2], "created": r[4]} for r in rows])

@app.route("/agents", methods=['GET', 'POST'])
@require_auth
def agents():
    if request.method == 'POST':
        data = request.json
        if not data or 'name' not in data:
            return jsonify({'error': 'Missing name'}), 400
        with sqlite3.connect('data/a1os.db') as conn:
            cur = conn.execute("INSERT INTO agents (name, type, status, metadata, created, last_active) VALUES (?, ?, ?, ?, ?, ?)",
                               (data['name'], data.get('type', 'worker'), 'idle', json.dumps(data.get('metadata', {})), datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
            return jsonify({"id": cur.lastrowid, "ok": True})
    with sqlite3.connect('data/a1os.db') as conn:
        rows = conn.execute("SELECT * FROM agents").fetchall()
        return jsonify([{"id": r[0], "name": r[1], "type": r[2], "status": r[3], "created": r[5]} for r in rows])

@app.route("/agents/<int:aid>/goal", methods=['POST'])
@require_auth
def agent_goal(aid):
    data = request.json
    if not data or 'goal' not in data:
        return jsonify({'error': 'Missing goal'}), 400
    with sqlite3.connect('data/a1os.db') as conn:
        conn.execute("INSERT INTO agent_goals (agent_id, description, status, created) VALUES (?, ?, ?, ?)",
                     (aid, data['goal'], 'pending', datetime.now().isoformat()))
        conn.commit()
        return jsonify({"ok": True})

@app.route("/agents/<int:aid>/logs", methods=['GET'])
@require_auth
def agent_logs(aid):
    with sqlite3.connect('data/a1os.db') as conn:
        rows = conn.execute("SELECT * FROM agent_logs WHERE agent_id = ? ORDER BY created DESC LIMIT 10", (aid,)).fetchall()
        return jsonify([{"log": r[2], "created": r[3]} for r in rows])

@app.route("/cluster/nodes", methods=['GET', 'POST'])
@require_auth
def cluster():
    if request.method == 'POST':
        data = request.json
        if not data or 'address' not in data:
            return jsonify({'error': 'Missing address'}), 400
        with sqlite3.connect('data/a1os.db') as conn:
            cur = conn.execute("INSERT INTO cluster_nodes (address, status, metadata, joined, last_heartbeat) VALUES (?, ?, ?, ?, ?)",
                               (data['address'], 'active', json.dumps(data.get('metadata', {})), datetime.now().isoformat(), datetime.now().isoformat()))
            conn.commit()
            return jsonify({"id": cur.lastrowid, "ok": True})
    with sqlite3.connect('data/a1os.db') as conn:
        rows = conn.execute("SELECT * FROM cluster_nodes").fetchall()
        return jsonify([{"id": r[0], "address": r[1], "status": r[2], "joined": r[4]} for r in rows])

@app.route("/cluster/leader", methods=['GET'])
@require_auth
def cluster_leader():
    with sqlite3.connect('data/a1os.db') as conn:
        row = conn.execute("SELECT id FROM cluster_nodes WHERE status = 'active' LIMIT 1").fetchone()
        return jsonify({"leader": row[0] if row else None})

@app.route("/consensus/propose", methods=['POST'])
@require_auth
def consensus_propose():
    data = request.json
    if not data or 'proposal' not in data:
        return jsonify({'error': 'Missing proposal'}), 400
    with sqlite3.connect('data/a1os.db') as conn:
        term = conn.execute("SELECT MAX(term) FROM consensus_log").fetchone()[0] or 0
        term += 1
        conn.execute("INSERT INTO consensus_log (term, proposal, status, metadata, timestamp) VALUES (?, ?, ?, ?, ?)",
                     (term, data['proposal'], 'proposed', json.dumps(data.get('metadata', {})), datetime.now().isoformat()))
        conn.commit()
        return jsonify({"term": term, "ok": True})

@app.route("/consensus/log", methods=['GET'])
@require_auth
def consensus_log():
    with sqlite3.connect('data/a1os.db') as conn:
        rows = conn.execute("SELECT * FROM consensus_log ORDER BY term DESC").fetchall()
        return jsonify([{"term": r[1], "proposal": r[2], "status": r[3], "timestamp": r[5]} for r in rows])

@app.route("/consensus/vote/<int:log_id>", methods=['POST'])
@require_auth
def consensus_vote(log_id):
    data = request.json
    if not data or 'vote' not in data:
        return jsonify({'error': 'Missing vote'}), 400
    with sqlite3.connect('data/a1os.db') as conn:
        conn.execute("UPDATE consensus_log SET status = ? WHERE id = ?", ('committed' if data['vote'] else 'rejected', log_id))
        conn.commit()
        return jsonify({"ok": True})

@app.route("/scheduler/tasks", methods=['GET', 'POST'])
@require_auth
def scheduler():
    if request.method == 'POST':
        data = request.json
        if not data or 'name' not in data or 'action' not in data:
            return jsonify({'error': 'Missing name or action'}), 400
        with sqlite3.connect('data/a1os.db') as conn:
            cur = conn.execute("INSERT INTO tasks (name, schedule, action, status, created) VALUES (?, ?, ?, ?, ?)",
                               (data['name'], data.get('schedule', 'once'), data['action'], 'pending', datetime.now().isoformat()))
            conn.commit()
            return jsonify({"id": cur.lastrowid, "ok": True})
    with sqlite3.connect('data/a1os.db') as conn:
        rows = conn.execute("SELECT * FROM tasks").fetchall()
        return jsonify([{"id": r[0], "name": r[1], "schedule": r[2], "action": r[3], "status": r[4], "created": r[5]} for r in rows])

@app.route("/knowledge", methods=['GET', 'POST'])
@require_auth
def knowledge():
    if request.method == 'POST':
        data = request.json
        if not data or 'key' not in data or 'value' not in data:
            return jsonify({'error': 'Missing key or value'}), 400
        with sqlite3.connect('data/a1os.db') as conn:
            conn.execute("INSERT OR REPLACE INTO knowledge (key, value, metadata, updated) VALUES (?, ?, ?, ?)",
                         (data['key'], data['value'], json.dumps(data.get('metadata', {})), datetime.now().isoformat()))
            conn.commit()
            return jsonify({"ok": True})
    with sqlite3.connect('data/a1os.db') as conn:
        rows = conn.execute("SELECT * FROM knowledge").fetchall()
        return jsonify([{"key": r[0], "value": r[1], "updated": r[3]} for r in rows])

@app.route("/events", methods=['GET'])
@require_auth
def events():
    with sqlite3.connect('data/a1os.db') as conn:
        rows = conn.execute("SELECT * FROM events ORDER BY time DESC LIMIT 20").fetchall()
        return jsonify([{"type": r[1], "data": r[2], "time": r[3]} for r in rows])

@app.route("/system/status", methods=['GET'])
@require_auth
def system_status():
    with sqlite3.connect('data/a1os.db') as conn:
        return jsonify({
            "status": "online",
            "version": "A1OS v2.0",
            "modules": ["memory", "agents", "cluster", "consensus", "scheduler", "knowledge", "events", "system"]
        })

@app.route("/observability/metrics", methods=['GET'])
@require_auth
def obs_metrics():
    with sqlite3.connect('data/a1os.db') as conn:
        return jsonify({
            "timestamp": datetime.now().isoformat(),
            "memory": conn.execute("SELECT COUNT(*) FROM memory").fetchone()[0] or 0,
            "agents": conn.execute("SELECT COUNT(*) FROM agents").fetchone()[0] or 0,
            "tasks": conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] or 0,
            "knowledge": conn.execute("SELECT COUNT(*) FROM knowledge").fetchone()[0] or 0,
            "cluster_nodes": conn.execute("SELECT COUNT(*) FROM cluster_nodes").fetchone()[0] or 0,
            "consensus_entries": conn.execute("SELECT COUNT(*) FROM consensus_log").fetchone()[0] or 0
        })

@app.route("/observability/health", methods=['GET'])
@require_auth
def obs_health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/domain/packs", methods=['GET'])
@require_auth
def domain_packs():
    from domain_packs.loader import DomainPackLoader
    loader = DomainPackLoader()
    return jsonify({"packs": loader.list_available()})

@app.route("/domain/packs/<name>", methods=['GET'])
@require_auth
def domain_pack_info(name):
    from domain_packs.loader import DomainPackLoader
    loader = DomainPackLoader()
    return jsonify(loader.load(name))

@app.route("/production/status", methods=['GET'])
@require_auth
def prod_status():
    return jsonify({"status": "online", "version": "A1OS v2.0", "environment": "production"})

@app.route("/production/backup", methods=['POST'])
@require_auth
def prod_backup():
    import subprocess
    try:
        subprocess.run(["./scripts/backup.sh"], capture_output=True, timeout=30)
        return jsonify({"ok": True})
    except:
        return jsonify({"ok": False}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086)
