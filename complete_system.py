from security_fix import limiter, validate_input
import sys
sys.path.insert(0, ".")

from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
import secrets
import sqlite3
import json
from datetime import datetime

from api.memory_routes import register_memory_routes
from api.knowledge_routes import register_knowledge_routes
from api.scheduler_routes import register_scheduler_routes
from api.agents_routes import register_agents_routes
from api.cluster_routes import register_cluster_routes
from api.consensus_routes import register_consensus_routes
from api.system_routes import register_system_routes
from api.workflow_routes import register_workflow_routes
from api.domain_routes import register_domain_routes

app = Flask(__name__)
CORS(app, origins=["http://localhost:8000"])

# ===== DATABASE =====
def get_db():
    conn = sqlite3.connect('data/a1os.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY, username TEXT UNIQUE, password_hash TEXT, api_key TEXT, created TEXT
            );
            CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, text TEXT, tags TEXT, created TEXT);
        ''')
init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def generate_api_key():
    return secrets.token_hex(32)

with get_db() as conn:
    existing = conn.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
    if not existing:
        api_key = generate_api_key()
        conn.execute("INSERT INTO users (id, username, password_hash, api_key, created) VALUES (?, ?, ?, ?, ?)",
                     ("user_1", "admin", hash_password("admin123"), api_key, datetime.now().isoformat()))
        conn.commit()

# ===== ROUTES =====
@app.route("/")
def root():
    return jsonify({
        "status": "online",
        "version": "A1OS v2.0",
        "modules": ["memory", "knowledge", "scheduler", "agents", "cluster", "consensus", "events", "system", "auth"],
        "timestamp": datetime.now().isoformat()
    })

@limiter.limit("5 per minute")
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Missing username or password"}), 400
    with get_db() as conn:
        existing = conn.execute("SELECT * FROM users WHERE username = ?", (data["username"],)).fetchone()
        if existing:
            return jsonify({"error": "Username already exists"}), 409
        api_key = generate_api_key()
        conn.execute("INSERT INTO users (id, username, password_hash, api_key, created) VALUES (?, ?, ?, ?, ?)",
                     (f"user_{secrets.token_hex(8)}", data["username"], hash_password(data["password"]), api_key, datetime.now().isoformat()))
        conn.commit()
        return jsonify({"ok": True, "api_key": api_key})

@limiter.limit("5 per minute")
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Missing username or password"}), 400
    with get_db() as conn:
        user = conn.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?",
                            (data["username"], hash_password(data["password"]))).fetchone()
        if not user:
            return jsonify({"error": "Invalid credentials"}), 401
        return jsonify({"ok": True, "api_key": user["api_key"]})

# ===== REGISTER ALL MODULES =====
register_memory_routes(app)
register_knowledge_routes(app)
register_scheduler_routes(app)
register_agents_routes(app)
register_cluster_routes(app)
register_consensus_routes(app)
register_system_routes(app)
register_workflow_routes(app)
register_domain_routes(app)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8086, debug=False)
