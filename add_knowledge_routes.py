with open('final_hybrid.py', 'r') as f:
    content = f.read()

routes = '''
@app.route("/knowledge", methods=["GET", "POST"])
def knowledge_route():
    if request.method == "POST":
        data = request.json
        if not data or "key" not in data or "value" not in data:
            return jsonify({"error": "Missing key or value"}), 400
        with sqlite3.connect('data/a1os.db') as conn:
            conn.execute("INSERT OR REPLACE INTO knowledge (key, value, updated) VALUES (?, ?, ?)",
                         (data["key"], data["value"], datetime.now().isoformat()))
            conn.commit()
            return jsonify({"ok": True})
    with sqlite3.connect('data/a1os.db') as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM knowledge").fetchall()
        return jsonify([dict(r) for r in rows])
'''

# Remove duplicate knowledge route if exists
import re
content = re.sub(r'@app\.route\("/knowledge", methods=\["GET", "POST"\]\).*?return jsonify\(\[dict\(r\) for r in rows\]\)\n', '', content, flags=re.DOTALL)

insert_point = content.find('@app.route("/consensus/vote"')
if insert_point == -1:
    insert_point = content.find('@app.route("/system/status"')
content = content[:insert_point] + routes + content[insert_point:]

with open('final_hybrid.py', 'w') as f:
    f.write(content)
print('✅ Knowledge routes added')
