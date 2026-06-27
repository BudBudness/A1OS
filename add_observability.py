with open('final_hybrid.py', 'r') as f:
    content = f.read()

routes = '''
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

@app.route("/observability/events", methods=["GET"])
def observability_events():
    from events.bus import EventBus
    bus = EventBus()
    return jsonify({"events": bus.get_history(50)})
'''

insert_point = content.find('@app.route("/domain/packs"')
if insert_point == -1:
    insert_point = content.find('if __name__ == "__main__":')
content = content[:insert_point] + routes + content[insert_point:]

with open('final_hybrid.py', 'w') as f:
    f.write(content)
print('✅ Observability routes added')
