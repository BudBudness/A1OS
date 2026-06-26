from flask import request, jsonify
from knowledge.engine import KnowledgeEngine

knowledge = KnowledgeEngine()

def register_knowledge_routes(app):
    @app.route('/knowledge', methods=['GET', 'POST'])
    def knowledge_endpoint():
        if request.method == 'POST':
            data = request.json
            if not data or 'key' not in data or 'value' not in data:
                return jsonify({'error': 'Missing key or value'}), 400
            knowledge.set(data['key'], data['value'], data.get('metadata'))
            return jsonify({'ok': True})
        return jsonify(knowledge.get_all())

    @app.route('/knowledge/<key>', methods=['GET', 'DELETE'])
    def knowledge_item(key):
        if request.method == 'DELETE':
            knowledge.delete(key)
            return jsonify({'ok': True})
        item = knowledge.get(key)
        if not item:
            return jsonify({'error': 'Not found'}), 404
        return jsonify(item)
