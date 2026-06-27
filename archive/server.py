from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
from datetime import datetime

app = Flask(__name__)
CORS(app)

memory = {}
agents = {"agent_1": {"name": "Orchestrator", "status": "idle"}}
tasks = []
knowledge = {}
events = []

@app.route("/")
def root():
    return jsonify({"status": "online", "modules": ["memory", "agents", "tasks", "knowledge"]})

@app.route("/memory", methods=["GET", "POST"])
def memory_endpoint():
    if request.method == "POST":
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "Missing text"}), 400
        mid = hashlib.md5(data["text"].encode()).hexdigest()
        memory[mid] = {"id": mid, "text": data["text"], "created": datetime.now().isoformat()}
        events.append({"type": "memory_add", "data": mid})
        return jsonify({"ok": True, "id": mid})
    return jsonify(list(memory.values()))

@app.route("/memory/search")
def search():
    q = request.args.get("q", "").lower()
    if not q:
        return jsonify(list(memory.values()))
    results = [m for m in memory.values() if q in m["text"].lower()]
    return jsonify(results)

@app.route("/agents")
def list_agents():
    return jsonify(agents)

@app.route("/tasks", methods=["GET", "POST"])
def tasks_endpoint():
    if request.method == "POST":
        data = request.json
        if not data or "task" not in data:
            return jsonify({"error": "Missing task"}), 400
        tasks.append({"id": len(tasks)+1, "task": data["task"], "status": "pending"})
        return jsonify({"ok": True, "id": len(tasks)})
    return jsonify(tasks)

@app.route("/knowledge", methods=["GET", "POST"])
def knowledge_endpoint():
    if request.method == "POST":
        data = request.json
        if not data or "key" not in data or "value" not in data:
            return jsonify({"error": "Missing key/value"}), 400
        knowledge[data["key"]] = {"value": data["value"], "updated": datetime.now().isoformat()}
        return jsonify({"ok": True})
    return jsonify(knowledge)

@app.route("/events")
def get_events():
    return jsonify({"events": events[-20:]})

@app.route("/status")
def status():
    return jsonify({
        "memory": len(memory),
        "agents": len(agents),
        "tasks": len(tasks),
        "knowledge": len(knowledge),
        "events": len(events)
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086)
