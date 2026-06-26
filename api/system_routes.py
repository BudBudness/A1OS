from flask import request, jsonify
from system.health import HealthCheck

health = HealthCheck()

def register_system_routes(app):
    @app.route('/system/health', methods=['GET'])
    def system_health():
        return jsonify(health.check())

    @app.route('/system/status', methods=['GET'])
    def system_status():
        return jsonify({
            'status': 'online',
            'version': 'A1OS v2.0',
            'modules': ['memory', 'knowledge', 'scheduler', 'agents', 'cluster', 'consensus', 'events', 'system']
        })
