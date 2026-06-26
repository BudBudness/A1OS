from flask import request, jsonify
from cluster.engine import ClusterEngine

cluster = ClusterEngine()

def register_cluster_routes(app):
    @app.route('/cluster/nodes', methods=['GET', 'POST'])
    def cluster_endpoint():
        if request.method == 'POST':
            data = request.json
            if not data or 'address' not in data:
                return jsonify({'error': 'Missing address'}), 400
            result = cluster.add_node(data['address'], data.get('metadata'))
            return jsonify(result)
        return jsonify(cluster.get_nodes())

    @app.route('/cluster/nodes/<int:node_id>/heartbeat', methods=['POST'])
    def cluster_heartbeat(node_id):
        cluster.heartbeat(node_id)
        return jsonify({'ok': True})

    @app.route('/cluster/leader', methods=['GET'])
    def cluster_leader():
        return jsonify({'leader': cluster.leader})
