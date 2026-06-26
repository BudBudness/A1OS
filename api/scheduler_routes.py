from flask import request, jsonify
from scheduler.engine import SchedulerEngine

scheduler = SchedulerEngine()

def register_scheduler_routes(app):
    @app.route('/scheduler/tasks', methods=['GET', 'POST'])
    def scheduler_endpoint():
        if request.method == 'POST':
            data = request.json
            if not data or 'name' not in data or 'schedule' not in data or 'action' not in data:
                return jsonify({'error': 'Missing name, schedule, or action'}), 400
            result = scheduler.add(data['name'], data['schedule'], data['action'], data.get('metadata'))
            return jsonify(result)
        return jsonify(scheduler.get_all())

    @app.route('/scheduler/tasks/<int:task_id>/run', methods=['POST'])
    def run_task(task_id):
        result = scheduler.run_task(task_id)
        return jsonify(result)
