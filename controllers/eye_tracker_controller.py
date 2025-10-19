from flask import jsonify


class EyeTrackerController:
    def __init__(self,eye_tracking_service):
        self.eye_tracking_service = eye_tracking_service

    def get_eye_coordinates(self):
        """ get coordinates of the eye """
        eye_data = self.eye_tracking_service.get_eye_data()
        return jsonify(eye_data)
    
    def start_tracking(self, socketio_instance):
        """ start eye tracking """
        success = self.eye_tracking_service.start_tracking(socketio_instance)
        return jsonify({
            'success': success,
            'message': 'Eye tracking started' if success else 'Failed to start tracking'
        })
    
    def stop_tracking(self):
        """stop eye tracking"""
        self.eye_tracking_service.stop_tracking()
        return jsonify({
            'success': True,
            'message': 'Eye tracking stopped'
        })
    
    def emergency_stop(self):
        """emegegency fails safe"""
        self.eye_tracking_service.stop_tracking()
        return jsonify({
            'success': True,
            'message': 'Emergency stop activated'
        })
    
    def get_system_status(self):
        """ get system status """
        return jsonify({
            'camera_available': self.eye_tracking_service.is_camera_available(),
            'tracking_active': self.eye_tracking_service.tracking_active
        })