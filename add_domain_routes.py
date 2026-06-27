with open('final_hybrid.py', 'r') as f:
    content = f.read()

routes = '''
# ===== DOMAIN PACK ROUTES =====
@app.route("/domain/packs", methods=["GET"])
def domain_packs():
    from domain_packs.loader import DomainPackLoader
    loader = DomainPackLoader()
    return jsonify({"packs": loader.list_available()})

@app.route("/domain/packs/<name>", methods=["GET"])
def domain_pack_info(name):
    from domain_packs.loader import DomainPackLoader
    loader = DomainPackLoader()
    pack = loader.load(name)
    return jsonify(pack)

@app.route("/domain/packs/<name>/activate", methods=["POST"])
def domain_pack_activate(name):
    from domain_packs.loader import DomainPackLoader
    loader = DomainPackLoader()
    pack = loader.load(name)
    return jsonify({"ok": True, "pack": name, "status": "active"})
'''

insert_point = content.find('@app.route("/api/v1/modules")')
if insert_point == -1:
    insert_point = content.find('if __name__ == "__main__":')
content = content[:insert_point] + routes + content[insert_point:]

with open('final_hybrid.py', 'w') as f:
    f.write(content)
print('✅ Domain Pack routes added')
