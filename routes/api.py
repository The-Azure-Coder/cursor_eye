from flask import Blueprint

def create_api_blueprint(eye_tracker_controller, socketio_instance):
    """"Create Api blueprint with dependency injection"""
    api_bp = Blueprint('api', __name__)

    @api_bp.route('/api/eye-coordinates', methods=['GET'])
    def get_eye_coordinates():
        return eye_tracker_controller.get_eye_coordinates()
    
    @api_bp.route('/api/control/start', methods=['POST'])
    def start_tracking():
        return eye_tracker_controller.start_tracking(socketio_instance)
    
    @api_bp.route('/api/control/stop', methods=['POST'])
    def stop_tracking():
        return eye_tracker_controller.stop_tracking()
    
    @api_bp.route('/api/control/emergency-stop', methods=['POST'])
    def emergency_stop():
        return eye_tracker_controller.emergency_stop()
    
    @api_bp.route('/api/status', methods=['GET'])
    def get_system_status():
        return eye_tracker_controller.get_system_status()
    
    return api_bp