from flask import Flask, request, jsonify
from a1os.memory.vector_store import search, add
from a1os.ingest.pipeline import run as ingest_run

app=Flask(__name__)

@app.route("/")
def home():
    return "A1OS PHASE 1 ACTIVE"

@app.route("/search")
def s():
    q=request.args.get("q","")
    return jsonify(search(q))

@app.route("/add",methods=["POST"])
def a():
    add(request.json["text"])
    return jsonify({"ok":True})

@app.route("/ingest")
def i():
    ingest_run()
    return jsonify({"ingested":True})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=8086)
