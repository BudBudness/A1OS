#!/bin/bash
echo "🚀 Generating Stages 4-7..."

# Stage 4: Flutter Mobile
mkdir -p ui/flutter/lib
cat > ui/flutter/lib/main.dart << 'DART'
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

void main() => runApp(A1OSApp());

class A1OSApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'A1OS',
    theme: ThemeData.dark(),
    home: Dashboard(),
  );
}

class Dashboard extends StatefulWidget {
  @override
  _DashboardState createState() => _DashboardState();
}

class _DashboardState extends State<Dashboard> {
  var data = {};
  final apiKey = 'e6d4f897ff9934ed5d61309bf1286436f96c0dd55a9c7b42b921c2936011267d';

  @override
  void initState() {
    super.initState();
    fetchStatus();
  }

  Future<void> fetchStatus() async {
    try {
      final res = await http.get(
        Uri.parse('http://localhost:8086/system/status'),
        headers: {'X-API-Key': apiKey},
      );
      setState(() => data = jsonDecode(res.body));
    } catch(e) { print(e); }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: Text('A1OS v2.0')),
    body: Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          Text('Status: ${data['status'] ?? 'loading...'}'),
          Text('Version: ${data['version'] ?? '...'}'),
          Text('Modules: ${(data['modules'] ?? []).join(', ')}'),
        ],
      ),
    ),
  );
}
DART

# Stage 5: Workflow Engine
mkdir -p workflows
cat > workflows/engine.py << 'PY'
from typing import List, Dict, Any
import json
import sqlite3
from datetime import datetime

class WorkflowEngine:
    def __init__(self, db_path: str = "data/a1os.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    steps TEXT,
                    status TEXT,
                    created TEXT,
                    completed TEXT
                )
            ''')

    def create(self, name: str, steps: List[Dict]) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "INSERT INTO workflows (name, steps, status, created) VALUES (?, ?, ?, ?)",
                (name, json.dumps(steps), "pending", datetime.now().isoformat())
            )
            conn.commit()
            return {"id": cur.lastrowid, "name": name, "status": "pending"}

    def get_all(self) -> List[Dict]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM workflows").fetchall()
            return [{"id": r[0], "name": r[1], "steps": json.loads(r[2]), "status": r[3], "created": r[4], "completed": r[5]} for r in rows]

    def execute(self, workflow_id: int) -> Dict:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE workflows SET status = 'running', completed = ? WHERE id = ?", (datetime.now().isoformat(), workflow_id))
            conn.commit()
        # Simulate execution
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("UPDATE workflows SET status = 'completed' WHERE id = ?", (workflow_id,))
            conn.commit()
        return {"ok": True, "id": workflow_id}
PY

# Stage 6: Domain Packs
mkdir -p domain_packs
cat > domain_packs/loader.py << 'PY'
import importlib
import os
from typing import Dict, Any

class DomainPackLoader:
    def __init__(self, packs_dir: str = "domain_packs"):
        self.packs_dir = packs_dir
        self.loaded = {}

    def load(self, pack_name: str) -> Dict[str, Any]:
        if pack_name in self.loaded:
            return self.loaded[pack_name]
        try:
            module = importlib.import_module(f"domain_packs.{pack_name}")
            self.loaded[pack_name] = {"name": pack_name, "module": module, "loaded": True}
            return self.loaded[pack_name]
        except ImportError:
            return {"name": pack_name, "error": "Not found", "loaded": False}

    def list_available(self) -> list:
        files = os.listdir(self.packs_dir)
        return [f[:-3] for f in files if f.endswith('.py') and not f.startswith('__')]
PY

# Stage 7: Production Deployment
cat > deploy/production.sh << 'SH'
#!/bin/bash
echo "🚀 Production Deployment"
mkdir -p /tmp/a1os_prod
cp -r api core memory knowledge agents scheduler cluster consensus events system workflows domain_packs config data /tmp/a1os_prod/
cd /tmp/a1os_prod
nohup python3 -m api.server > /var/log/a1os.log 2>&1 &
echo "A1OS deployed to /tmp/a1os_prod"
SH
chmod +x deploy/production.sh

echo "✅ Stages 4-7 generated"
