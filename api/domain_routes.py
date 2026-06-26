from flask import request, jsonify
from domain_packs.loader import DomainPackLoader

loader = DomainPackLoader()

def register_domain_routes(app):
    @app.route('/domain/packs', methods=['GET'])
    def list_packs():
        return jsonify({'packs': loader.list_available()})

    @app.route('/domain/packs/<name>/load', methods=['POST'])
    def load_pack(name):
        result = loader.load(name)
        return jsonify(result)
