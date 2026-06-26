from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import json, hashlib, time, threading, queue, os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ===== STATE =====
memory_store = {}
agents = {}
agent_goals = {}
agent_logs = {}
cluster_nodes = {}
cluster_leader = None
consensus_log = []
consensus_term = 0
scheduled_tasks = []
task_id = 0
knowledge_base = {}
event_queue = queue.Queue()
event_history = []

def log_event(etype, data):
    entry = {"time": datetime.now().isoformat(), "type": etype, "data": data}
    event_history.append(entry)
    if len(event_history) > 100: event_history.pop(0)
    event_queue.put(entry)

# ===== INIT =====
# Create default agent
agents["agent_1"] = {
    "id": "agent_1",
    "name": "A1OS-Orchestrator",
    "type": "orchestrator",
    "status": "idle",
    "created": datetime.now().isoformat()
}
agent_goals["agent_1"] = []
agent_logs["agent_1"] = []

# Create default cluster node
cluster_nodes["node_1"] = {
    "id": "node_1",
    "address": "localhost:8086",
    "status": "active",
    "joined": datetime.now().isoformat()
}
cluster_leader = "node_1"

log_event("system_init", {"message": "A1OS initialized with default agent and cluster node"})

# ===== ROOT =====
@app.route("/")
def root():
    return jsonify({
        "status": "online",
        "version": "A1OS v2.0",
        "modules": ["memory", "agents", "cluster", "consensus", "scheduler", "knowledge", "events", "system"],
        "timestamp": datetime.now().isoformat()
    })

# ===== MEMORY =====
@app.route("/memory", methods=["GET", "POST"])
def memory():
    if request.method == "POST":
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "Missing text"}), 400
        doc_id = hashlib.md5(data["text"].encode()).hexdigest()
        memory_store[doc_id] = {
            "id": doc_id,
            "text": data["text"],
            "tags": data.get("tags", []),
            "created": datetime.now().isoformat()
        }
        log_event("memory_add", {"id": doc_id})
        return jsonify({"ok": True, "id": doc_id})
    return jsonify(list(memory_store.values()))

@app.route("/memory/search")
def memory_search():
    q = request.args.get("q", "").lower()
    if not q:
        return jsonify(list(memory_store.values()))
    results = []
    for doc in memory_store.values():
        score = sum(1 for w in q.split() if w in doc["text"].lower())
        if score:
            results.append({"doc": doc, "score": score})
    results.sort(key=lambda x: x["score"], reverse=True)
    return jsonify([r["doc"] for r in results[:20]])

# ===== AGENTS =====
@app.route("/agents", methods=["GET", "POST"])
def agents_endpoint():
    if request.method == "POST":
        data = request.json
        if not data or "name" not in data:
            return jsonify({"error": "Missing name"}), 400
        aid = f"agent_{len(agents)+1}"
        agents[aid] = {
            "id": aid,
            "name": data["name"],
            "type": data.get("type", "general"),
            "status": "idle",
            "created": datetime.now().isoformat()
        }
        agent_goals[aid] = []
        agent_logs[aid] = []
        log_event("agent_created", {"id": aid})
        return jsonify({"ok": True, "id": aid})
    return jsonify(agents)

@app.route("/agents/<aid>/goal", methods=["POST"])
def set_goal(aid):
    if aid not in agents:
        return jsonify({"error": "Agent not found"}), 404
    data = request.json
    if not data or "goal" not in data:
        return jsonify({"error": "Missing goal"}), 400
    goal = {
        "id": f"goal_{len(agent_goals[aid])+1}",
        "description": data["goal"],
        "status": "pending",
        "created": datetime.now().isoformat()
    }
    agent_goals[aid].append(goal)
    agents[aid]["status"] = "working"
    log_event("agent_goal_set", {"agent": aid})
    return jsonify({"ok": True, "goal": goal})

@app.route("/agents/<aid>/status")
def agent_status(aid):
    if aid not in agents:
        return jsonify({"error": "Not found"}), 404
    return jsonify({
        "agent": agents[aid],
        "goals": agent_goals.get(aid, []),
        "logs": agent_logs.get(aid, [])[-10:]
    })

# ===== CLUSTER =====
@app.route("/cluster/nodes", methods=["GET", "POST"])
def cluster():
    global cluster_leader
    if request.method == "POST":
        data = request.json
        if not data or "address" not in data:
            return jsonify({"error": "Missing address"}), 400
        nid = f"node_{len(cluster_nodes)+1}"
        cluster_nodes[nid] = {
            "id": nid,
            "address": data["address"],
            "status": "active",
            "joined": datetime.now().isoformat()
        }
        if not cluster_leader:
            cluster_leader = nid
        log_event("node_joined", {"id": nid})
        return jsonify({"ok": True, "id": nid})
    return jsonify({"nodes": cluster_nodes, "leader": cluster_leader})

# ===== CONSENSUS =====
@app.route("/consensus", methods=["GET", "POST"])
def consensus():
    global consensus_term, consensus_log
    if request.method == "POST":
        data = request.json
        if not data or "proposal" not in data:
            return jsonify({"error": "Missing proposal"}), 400
        consensus_term += 1
        entry = {
            "term": consensus_term,
            "proposal": data["proposal"],
            "status": "proposed",
            "timestamp": datetime.now().isoformat()
        }
        consensus_log.append(entry)
        log_event("consensus_proposal", {"term": consensus_term})
        return jsonify({"ok": True, "term": consensus_term})
    return jsonify({"log": consensus_log, "term": consensus_term})

# ===== SCHEDULER =====
@app.route("/scheduler/tasks", methods=["GET", "POST"])
def scheduler():
    global task_id, scheduled_tasks
    if request.method == "POST":
        data = request.json
        if not data or "task" not in data:
            return jsonify({"error": "Missing task"}), 400
        task_id += 1
        task = {
            "id": task_id,
            "task": data["task"],
            "schedule": data.get("schedule", "once"),
            "status": "pending",
            "created": datetime.now().isoformat()
        }
        scheduled_tasks.append(task)
        log_event("task_scheduled", {"id": task_id})
        return jsonify({"ok": True, "id": task_id})
    return jsonify(scheduled_tasks)

@app.route("/scheduler/tasks/<int:tid>/run", methods=["POST"])
def run_task(tid):
    for t in scheduled_tasks:
        if t["id"] == tid:
            t["status"] = "running"
            log_event("task_running", {"id": tid})
            t["status"] = "completed"
            t["completed_at"] = datetime.now().isoformat()
            return jsonify({"ok": True})
    return jsonify({"error": "Not found"}), 404

# ===== KNOWLEDGE =====
@app.route("/knowledge", methods=["GET", "POST"])
def knowledge():
    if request.method == "POST":
        data = request.json
        if not data or "key" not in data or "value" not in data:
            return jsonify({"error": "Missing key/value"}), 400
        knowledge_base[data["key"]] = {
            "value": data["value"],
            "updated": datetime.now().isoformat()
        }
        log_event("knowledge_updated", {"key": data["key"]})
        return jsonify({"ok": True})
    return jsonify(knowledge_base)

# ===== EVENTS =====
@app.route("/events")
def events():
    return jsonify({"events": event_history[-20:]})

@app.route("/events/stream")
def event_stream():
    def gen():
        while True:
            try:
                yield f"data: {json.dumps(event_queue.get(timeout=30))}\n\n"
            except queue.Empty:
                yield "data: {}\n\n"
    return Response(gen(), mimetype="text/event-stream")

# ===== SYSTEM =====
@app.route("/system/status")
def system_status():
    return jsonify({
        "status": "online",
        "memory_count": len(memory_store),
        "agent_count": len(agents),
        "cluster_nodes": len(cluster_nodes),
        "cluster_leader": cluster_leader,
        "consensus_entries": len(consensus_log),
        "consensus_term": consensus_term,
        "tasks_pending": len([t for t in scheduled_tasks if t["status"] == "pending"]),
        "tasks_total": len(scheduled_tasks),
        "events_count": len(event_history),
        "knowledge_entries": len(knowledge_base),
        "uptime": datetime.now().isoformat()
    })

@app.route("/system/recover", methods=["POST"])
def recover():
    log_event("recovery_triggered", {})
    return jsonify({"ok": True, "message": "Recovery initiated"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086, debug=False, threaded=True)
