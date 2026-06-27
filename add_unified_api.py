with open('final_hybrid.py', 'r') as f:
    content = f.read()

api_routes = '''
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

@app.route("/api/v1/modules")
def api_modules():
    return jsonify({
        "modules": ["memory", "agents", "workflows", "scheduler", "cluster", "consensus", "knowledge", "hardware"],
        "count": 8
    })
'''

insert_point = content.find('@app.route("/system/status"')
if insert_point == -1:
    insert_point = content.find('if __name__ == "__main__":')
content = content[:insert_point] + api_routes + content[insert_point:]

with open('final_hybrid.py', 'w') as f:
    f.write(content)
print('✅ Unified API added')
