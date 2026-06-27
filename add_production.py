with open('final_hybrid.py', 'r') as f:
    content = f.read()

routes = '''
# ===== PRODUCTION ROUTES =====
@app.route("/production/health", methods=["GET"])
def production_health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "uptime": "online",
        "version": "A1OS v2.0"
    })

@app.route("/production/backup", methods=["POST"])
def production_backup():
    import subprocess
    try:
        result = subprocess.run(["./scripts/backup.sh"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            return jsonify({"ok": True, "message": "Backup completed"})
        else:
            return jsonify({"ok": False, "error": result.stderr}), 500
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.route("/production/status")
def production_status():
    return jsonify({
        "status": "online",
        "version": "A1OS v2.0",
        "environment": os.getenv("A1OS_ENV", "development"),
        "debug": os.getenv("DEBUG", "false").lower() == "true"
    })
'''

insert_point = content.find('@app.route("/security/status"')
if insert_point == -1:
    insert_point = content.find('if __name__ == "__main__":')
content = content[:insert_point] + routes + content[insert_point:]

with open('final_hybrid.py', 'w') as f:
    f.write(content)
print('✅ Production routes added')
