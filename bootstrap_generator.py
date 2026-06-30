import json, os
from pathlib import Path

with open("schema/platform.json") as f:
    schema = json.load(f)

phases = {
    "phase1_api": '''
from flask import Flask, jsonify
app = Flask(__name__)

{api_routes}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port={port})
''',
    "phase2_queue": '''
import os, time, shutil
from pathlib import Path
QUEUE_ROOT = Path("queue")
for d in ["incoming", "processing", "complete", "failed", "retry", "archive"]:
    (QUEUE_ROOT / d).mkdir(parents=True, exist_ok=True)
print("✅ Queue directories created")
''',
    "phase3_node_watcher": '''
import time, subprocess
from pathlib import Path
WATCH_DIR = Path("{watch}")
EMIT_DIR = Path("{emit}")
while True:
    for f in WATCH_DIR.glob("*"):
        if f.is_file():
            print(f"Processing: {{f}}")
            (EMIT_DIR / f.name).touch()
            f.unlink()
    time.sleep(1)
''',
    "phase4_provider": '''
import requests, json
class Provider:
    def __init__(self, endpoint="{endpoint}"):
        self.endpoint = endpoint
    def generate(self, prompt):
        resp = requests.post(f"{{self.endpoint}}/api/generate", json={{"prompt": prompt}})
        return resp.json()
print("✅ Provider initialized")
''',
    "phase5_memory": '''
import sqlite3, json, hashlib
from datetime import datetime
DB_PATH = "data/memory.db"
def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS memory (id TEXT PRIMARY KEY, content TEXT, type TEXT, metadata TEXT, created TEXT)")
def store(content, mem_type="long_term"):
    doc_id = hashlib.md5(content.encode()).hexdigest()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR REPLACE INTO memory (id, content, type, metadata, created) VALUES (?, ?, ?, ?, ?)",
                     (doc_id, content, mem_type, "{{}}", datetime.now().isoformat()))
        conn.commit()
    return {"id": doc_id}
init_db()
print("✅ Memory engine initialized")
''',
    "phase6_full_build": '''
import os, shutil
from pathlib import Path
BUILD_ROOT = Path("build/generated")
for module in schema.get("modules", {{}}):
    (BUILD_ROOT / module).mkdir(parents=True, exist_ok=True)
print("✅ Full build structure created")
'''
}

enabled_modules = [mod for mod, cfg in schema.get("modules", {}).items() if cfg.get("enabled")]
api_routes = "\n".join([
    f'@app.route("/{mod}/stats")\ndef {mod}_stats():\n    return jsonify({{"status": "ok"}})'
    for mod in enabled_modules
])

port = schema.get("runtime", {}).get("port", 8086)
watch = schema.get("nodes", [{}])[0].get("watch", "artifacts/raw_memory")
emit = schema.get("nodes", [{}])[0].get("emit", "artifacts/vector_memory")
endpoint = schema.get("providers", {}).get("ollama", {}).get("endpoint", "http://localhost:11434")

for name, template in phases.items():
    try:
        content = template.format(
            api_routes=api_routes,
            port=port,
            watch=watch,
            emit=emit,
            endpoint=endpoint
        )
        output_path = Path(f"build/generated/{name}.py")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        print(f"✅ Generated: {output_path}")
    except KeyError as e:
        print(f"⚠️ {name} failed: missing key {e}")
        # Write the template as-is for debugging
        output_path = Path(f"build/generated/{name}.py")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(template)
        print(f"   Wrote raw template to {output_path} for inspection")

print("✅ Generation complete")
