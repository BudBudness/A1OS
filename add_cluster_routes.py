with open('final_hybrid.py', 'r') as f:
    content = f.read()

routes = '''
@app.route("/cluster/nodes", methods=["GET", "POST"])
def cluster_route():
    if request.method == "POST":
        data = request.json
        if not data or "address" not in data:
            return jsonify({"error": "Missing address"}), 400
        node = cluster_engine.add_node(data["address"], data.get("metadata", {}))
        return jsonify(node)
    nodes = cluster_engine.get_nodes()
    return jsonify(nodes)

@app.route("/cluster/leader")
def cluster_leader():
    return jsonify({"leader": cluster_engine.leader})

@app.route("/cluster/heartbeat", methods=["POST"])
def cluster_heartbeat():
    data = request.json
    if not data or "node_id" not in data:
        return jsonify({"error": "Missing node_id"}), 400
    cluster_engine.heartbeat(data["node_id"])
    return jsonify({"ok": True})

'''

insert_point = content.find('@app.route("/scheduler/tasks"')
if insert_point == -1:
    insert_point = content.find('@app.route("/system/status"')
content = content[:insert_point] + routes + content[insert_point:]

with open('final_hybrid.py', 'w') as f:
    f.write(content)
print('✅ Cluster routes added')
