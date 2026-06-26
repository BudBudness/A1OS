from flask import Flask, request, jsonify
from flask_cors import CORS
import hashlib
app = Flask(__name__)
CORS(app)
store = {}
@app.route("/")
def home():
    return "A1OS PHASE 1 ACTIVE"
@app.route("/search")
def search():
    q = request.args.get("q", "").lower()
    return jsonify([d for d in store.values() if q in d.get("text", "").lower()])
@app.route("/add", methods=["POST"])
def add():
    data = request.json
    if not data or "text" not in data:
        return jsonify({"error": "Missing text"}), 400
    doc_id = hashlib.md5(data["text"].encode()).hexdigest()
    store[doc_id] = {"id": doc_id, "text": data["text"]}
    return jsonify({"ok": True, "id": doc_id})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8086)
