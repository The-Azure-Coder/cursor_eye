from flask import Flask, render_template
from flask_socketio import SocketIO
from api.extensions import db
from config import config
from flask_cors import CORS

from services.eye_tracking_service import ets
from controllers.eye_tracker_controller import EyeTrackerController
from routes.api import create_api_blueprint
from api.server import createRestRoutes
# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = config.SQLALCHEMY_TRACK_MODIFICATIONS
# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", logger=False, engineio_logger=False)

db.init_app(app)
CORS(app)
# Database setup
# -----------------------------
#  Create database tables
# -----------------------------
with app.app_context():
    db.create_all()  # Creates all tables defined above if not existing

# Initialize services and controllers
eye_tracking_service = ets
eye_tracker_controller = EyeTrackerController(eye_tracking_service)

# Register API routes with dependency injection
api_bp = create_api_blueprint(eye_tracker_controller, socketio)
rest_bp = createRestRoutes()
app.register_blueprint(api_bp)
app.register_blueprint(rest_bp)
# WebSocket events
@socketio.on('connect')
def handle_connect():
    print("Client connected")
    socketio.emit('connected', {'status': 'success', 'message': 'Connected to eye tracker'})
    
    # Auto-start tracking when client connects (like your original code)
    if eye_tracking_service.is_camera_available() and not eye_tracking_service.tracking_active:
        eye_tracking_service.start_tracking(socketio)

@socketio.on('disconnect')
def handle_disconnect():
    print("❌ Client disconnected")

@socketio.on('emergency_stop')
def handle_emergency_stop():
    print("🛑 EMERGENCY STOP triggered by client")
    eye_tracking_service.stop_tracking()

# HTTP default routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/emergency_stop')
def emergency_stop_page():
    eye_tracking_service.stop_tracking()
    return """
    <html>
        <body style="background: red; color: white; text-align: center; padding: 50px;">
            <h1>🛑 EMERGENCY STOP ACTIVATED</h1>
            <p>Eye tracking has been disabled.</p>
            <p><a href="/" style="color: white;">Return to main page</a></p>
        </body>
    </html>
    """

if __name__ == '__main__':
    print("Starting Eye Tracker on http://localhost:5000")
    print(f"Webcam: {'Available' if eye_tracking_service.is_camera_available() else 'Unavailable'}")
    print("Eye tracking system ready!")
    print("Emergency stop: Visit http://localhost:5000/emergency_stop")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
    # t1 = threading.Thread(target= socketio.run(app, host='0.0.0.0', port=5000, debug=False))
    # t2 = threading.Thread(target= server.api_app.run("127.0.0.1",5050))

    # t1.start()
    # t2.start()

    # t1.join()
    # t2.join()

    
