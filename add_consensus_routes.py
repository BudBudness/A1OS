with open('final_hybrid.py', 'r') as f:
    content = f.read()

routes = '''
@app.route("/consensus/propose", methods=["POST"])
def consensus_propose():
    data = request.json
    if not data or "proposal" not in data:
        return jsonify({"error": "Missing proposal"}), 400
    result = consensus_engine.propose(data["proposal"], data.get("metadata", {}))
    return jsonify(result)

@app.route("/consensus/log")
def consensus_log():
    return jsonify(consensus_engine.get_log())

@app.route("/consensus/vote/<int:log_id>", methods=["POST"])
def consensus_vote():
    data = request.json
    if not data or "vote" not in data:
        return jsonify({"error": "Missing vote"}), 400
    consensus_engine.vote(log_id, data["vote"])
    return jsonify({"ok": True})
'''

insert_point = content.find('@app.route("/cluster/heartbeat"')
if insert_point == -1:
    insert_point = content.find('@app.route("/scheduler/tasks"')
content = content[:insert_point] + routes + content[insert_point:]

with open('final_hybrid.py', 'w') as f:
    f.write(content)
print('✅ Consensus routes added')
