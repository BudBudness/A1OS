from flask import request, jsonify
from workflows.engine import WorkflowEngine

workflow_engine = WorkflowEngine()

def register_workflow_routes(app):
    @app.route('/workflows', methods=['GET', 'POST'])
    def workflows():
        if request.method == 'POST':
            data = request.json
            if not data or 'name' not in data or 'steps' not in data:
                return jsonify({'error': 'Missing name or steps'}), 400
            result = workflow_engine.create(data['name'], data['steps'])
            return jsonify(result)
        return jsonify(workflow_engine.get_all())

    @app.route('/workflows/<int:wf_id>/execute', methods=['POST'])
    def execute_workflow(wf_id):
        result = workflow_engine.execute(wf_id)
        return jsonify(result)
