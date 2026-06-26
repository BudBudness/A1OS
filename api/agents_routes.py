from flask import request, jsonify
from agents.engine import AgentEngine

agents = AgentEngine()

def register_agents_routes(app):
    @app.route('/agents', methods=['GET', 'POST'])
    def agents_endpoint():
        if request.method == 'POST':
            data = request.json
            if not data or 'name' not in data:
                return jsonify({'error': 'Missing name'}), 400
            result = agents.create(data['name'], data.get('type', 'general'), data.get('metadata'))
            return jsonify(result)
        return jsonify(agents.get_all())

    @app.route('/agents/<int:agent_id>/status', methods=['PUT'])
    def agent_status(agent_id):
        data = request.json
        if not data or 'status' not in data:
            return jsonify({'error': 'Missing status'}), 400
        agents.update_status(agent_id, data['status'])
        return jsonify({'ok': True})
