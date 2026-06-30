
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/memory/stats")
def memory_stats():
    return jsonify({"status": "ok"})
@app.route("/agents/stats")
def agents_stats():
    return jsonify({"status": "ok"})
@app.route("/scheduler/stats")
def scheduler_stats():
    return jsonify({"status": "ok"})
@app.route("/knowledge/stats")
def knowledge_stats():
    return jsonify({"status": "ok"})
@app.route("/events/stats")
def events_stats():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086)
