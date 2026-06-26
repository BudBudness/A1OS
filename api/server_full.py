from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
from datetime import datetime
from memory.store import MemoryStore
from system.health import HealthCheck

app = Flask(__name__)
CORS(app)

memory = MemoryStore()
health = HealthCheck()

@app.route("/")
def root():
    return jsonify({"status": "online", "version": "A1OS v1.0", "modules": ["memory"]})

@app.route("/memory", methods=["GET", "POST"])
def memory_endpoint():
    if request.method == "POST":
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "Missing text"}), 400
        result = memory.add(data["text"])
        return jsonify({"ok": True, "id": result["id"]})
    return jsonify(memory.get_all())

@app.route("/health")
def health_check():
    return jsonify(health.check())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086)