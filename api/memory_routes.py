from flask import request, jsonify
from memory_intelligence.engine import MemoryEngine

memory_engine = MemoryEngine()

def register_memory_routes(app):
    @app.route('/memory/store', methods=['POST'])
    def memory_store():
        data = request.json
        if not data or 'content' not in data:
            return jsonify({'error': 'Missing content'}), 400
        mem_type = data.get('type', 'long_term')
        metadata = data.get('metadata', {})
        result = memory_engine.add(data['content'], mem_type, metadata)
        return jsonify({'ok': True, 'id': result.id})

    @app.route('/memory/search', methods=['GET'])
    def memory_search():
        query = request.args.get('q', '')
        if not query:
            return jsonify({'error': 'Missing query'}), 400
        results = memory_engine.search(query)
        return jsonify({'results': results})

    @app.route('/memory/retrieve', methods=['POST'])
    def memory_retrieve():
        data = request.json
        if not data or 'query' not in data:
            return jsonify({'error': 'Missing query'}), 400
        results = memory_engine.retrieve(data['query'], data.get('top_k', 20))
        return jsonify(results)

    @app.route('/memory/consolidate', methods=['POST'])
    def memory_consolidate():
        results = memory_engine.consolidate()
        return jsonify(results)

    @app.route('/memory/stats', methods=['GET'])
    def memory_stats():
        stats = memory_engine.get_stats()
        return jsonify({
            'total': stats.total,
            'working': stats.working,
            'episodic': stats.episodic,
            'long_term': stats.long_term,
            'vector': stats.vector,
            'graph_nodes': stats.graph_nodes,
            'graph_edges': stats.graph_edges,
            'avg_importance': stats.avg_importance
        })

    @app.route('/memory/graph', methods=['GET'])
    def memory_graph():
        relations = memory_engine.get_graph()
        return jsonify({'relations': relations})

    @app.route('/memory/relation', methods=['POST'])
    def memory_add_relation():
        data = request.json
        if not data or 'source' not in data or 'target' not in data or 'relation' not in data:
            return jsonify({'error': 'Missing source, target, or relation'}), 400
        memory_engine.add_relation(data['source'], data['target'], data['relation'], data.get('metadata', {}))
        return jsonify({'ok': True})
