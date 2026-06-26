from flask import request, jsonify
from consensus.engine import ConsensusEngine

consensus = ConsensusEngine()

def register_consensus_routes(app):
    @app.route('/consensus/propose', methods=['POST'])
    def consensus_propose():
        data = request.json
        if not data or 'proposal' not in data:
            return jsonify({'error': 'Missing proposal'}), 400
        result = consensus.propose(data['proposal'], data.get('metadata'))
        return jsonify(result)

    @app.route('/consensus/log', methods=['GET'])
    def consensus_log():
        return jsonify(consensus.get_log())

    @app.route('/consensus/vote/<int:log_id>', methods=['POST'])
    def consensus_vote(log_id):
        data = request.json
        if not data or 'vote' not in data:
            return jsonify({'error': 'Missing vote'}), 400
        consensus.vote(log_id, data['vote'])
        return jsonify({'ok': True})
