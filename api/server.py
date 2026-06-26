from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import logging
from datetime import datetime
from config.settings import Settings
from memory.engine import MemoryEngine

app = Flask(__name__)
CORS(app)
settings = Settings()
memory = MemoryEngine()
logging.basicConfig(level=logging.INFO)

@app.route("/")
def root():
    return jsonify({"status": "online", "version": "A1OS v1.0", "timestamp": datetime.now().isoformat()})

@app.route("/memory", methods=["GET", "POST"])
def memory_endpoint():
    if request.method == "POST":
        data = request.json
        if not data or "text" not in data:
            return jsonify({"error": "Missing text"}), 400
        result = memory.store(data["text"], data.get("tags", []))
        return jsonify({"ok": True, "id": result["id"]})
    return jsonify(memory.get_all())

@app.route("/memory/search")
def memory_search():
    q = request.args.get("q", "")
    return jsonify(memory.search(q) if q else memory.get_all())

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/status")
def status():
    return jsonify(memory.stats())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=settings.API_PORT)
