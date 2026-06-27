from flask import request, jsonify
import subprocess
import json
import os

def register_hardware_routes(app):
    @app.route('/hardware/camera', methods=['POST'])
    def hardware_camera():
        data = request.json or {}
        camera_id = data.get('camera', 0)
        filename = data.get('filename', f'/tmp/photo_{os.getpid()}.jpg')
        try:
            result = subprocess.run(['termux-camera-photo', '-c', str(camera_id), filename], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return jsonify({'error': result.stderr or 'Camera failed'}), 500
            return jsonify({'ok': True, 'file': filename})
        except FileNotFoundError:
            return jsonify({'error': 'termux-camera-photo not installed'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/hardware/mic', methods=['POST'])
    def hardware_mic():
        data = request.json or {}
        action = data.get('action', 'start')
        filename = data.get('filename', '/tmp/recording.mp3')
        try:
            if action == 'start':
                subprocess.Popen(['termux-microphone-record', '-f', filename], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return jsonify({'ok': True, 'status': 'recording', 'file': filename})
            elif action == 'stop':
                subprocess.run(['pkill', '-f', 'termux-microphone-record'], capture_output=True, timeout=2)
                return jsonify({'ok': True, 'status': 'stopped', 'file': filename})
            return jsonify({'error': 'Invalid action'}), 400
        except FileNotFoundError:
            return jsonify({'error': 'termux-microphone-record not installed'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/hardware/location', methods=['GET'])
    def hardware_location():
        try:
            result = subprocess.run(['termux-location'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return jsonify({'error': result.stderr or 'Location failed'}), 500
            return jsonify({'ok': True, 'location': json.loads(result.stdout)})
        except FileNotFoundError:
            return jsonify({'error': 'termux-location not installed'}), 500
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid location data'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/hardware/sensors', methods=['GET'])
    def hardware_sensors():
        try:
            result = subprocess.run(['termux-sensor', '-a'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return jsonify({'error': result.stderr or 'Sensors failed'}), 500
            return jsonify({'ok': True, 'sensors': json.loads(result.stdout)})
        except FileNotFoundError:
            return jsonify({'error': 'termux-sensor not installed'}), 500
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid sensor data'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/hardware/battery', methods=['GET'])
    def hardware_battery():
        try:
            result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, timeout=10)
            if result.returncode != 0:
                return jsonify({'error': result.stderr or 'Battery status failed'}), 500
            return jsonify({'ok': True, 'battery': json.loads(result.stdout)})
        except FileNotFoundError:
            return jsonify({'error': 'termux-battery-status not installed'}), 500
        except json.JSONDecodeError:
            return jsonify({'error': 'Invalid battery data'}), 500
        except Exception as e:
            return jsonify({'error': str(e)}), 500
