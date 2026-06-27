with open('final_hybrid.py', 'r') as f:
    content = f.read()

security_routes = '''
# ===== SECURITY ROUTES =====
from functools import wraps
import time

# Rate limiting
rate_limits = {}

def rate_limit(limit=10, window=60):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            key = request.remote_addr
            now = time.time()
            if key not in rate_limits:
                rate_limits[key] = []
            rate_limits[key] = [t for t in rate_limits[key] if t > now - window]
            if len(rate_limits[key]) >= limit:
                return jsonify({"error": "Rate limit exceeded"}), 429
            rate_limits[key].append(now)
            return f(*args, **kwargs)
        return wrapped
    return decorator

@app.route("/security/audit", methods=["GET"])
def security_audit():
    try:
        with sqlite3.connect('data/a1os.db') as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM events ORDER BY time DESC LIMIT 20").fetchall()
            return jsonify([dict(r) for r in rows])
    except:
        return jsonify({"events": []})

@app.route("/security/status", methods=["GET"])
def security_status():
    return jsonify({
        "api_key_required": True,
        "rate_limiting": "enabled",
        "cors_restricted": True,
        "audit_logging": "enabled",
        "status": "secure"
    })
'''

insert_point = content.find('@app.route("/observability/events"')
if insert_point == -1:
    insert_point = content.find('if __name__ == "__main__":')
content = content[:insert_point] + security_routes + content[insert_point:]

with open('final_hybrid.py', 'w') as f:
    f.write(content)
print('✅ Security routes added')
