from flask import Flask, jsonify
from a1os.bus.event_bus import bus

app=Flask(__name__)

@app.route("/")
def home():
    return "A1OS DASHBOARD ACTIVE"

@app.route("/events")
def events():
    return jsonify(list(bus.topics["events"]))

@app.route("/tasks")
def tasks():
    return jsonify(list(bus.topics["tasks"]))

@app.route("/health")
def health():
    return {"status":"ok","tasks":len(bus.topics["tasks"])}

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5000)
