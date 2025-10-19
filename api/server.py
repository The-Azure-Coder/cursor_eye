import uuid
from flask import request, jsonify
from flask import Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from api.extensions import db
from datetime import datetime, timezone, timedelta
from functools import wraps
import api.db_models as db_models
import jwt
from config import config
from services.eye_tracking_service import ets

def createRestRoutes():
    rest_bp = Blueprint('rest', __name__)




    @rest_bp.route("/rest/")
    def hello_world():
        return jsonify({"Data": "This is a test"})


    # Token required decorator
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('authorization')

            if not token:
                return jsonify({'message': 'Token is missing!'}), 401

            try:
                token_string = token.split(" ")[1]
                print(token_string)
                data = jwt.decode(token_string, config.SECRET_KEY, algorithms=["HS256"])
                current_user = db_models.User.query.filter_by(id=data['id']).first()
            except:
                return jsonify({'message': 'Token is invalid!'}), 401

            return f(current_user, *args, **kwargs)

        return decorated


    @rest_bp.route("/rest/auth/login",  methods=['POST'])
    def login():
        # Confirm the information that is passed to the api is valid
        # Find the user that matches the username or email.
        # Confirm that the password matches. 
        # Send a successful response. 

        if request.method == 'POST':
            data = request.json
            email = data['email']
            password = data['password']
            user = db_models.User.query.filter_by(email=email).first()

            if not user or not check_password_hash(user.password, password):
                return jsonify({'message': 'Invalid email or password'}), 401

            token = jwt.encode({'id': user.id, 'exp': datetime.now(timezone.utc) + timedelta(hours=1)}, 
                            config.SECRET_KEY, algorithm="HS256")
            print(user)
            userFound = {
                'firstName': user.first_name,
                'lastName': user.last_name,
                'email': user.email,
            }
            return jsonify({"message": "Successfully logged in", "data": {"accessToken": token, "user": userFound}})

        return


    @rest_bp.route("/rest/auth/register", methods=['POST'])
    def signUp(): 
        if request.method == 'POST':
            data = request.json
            first_name = data['firstName']
            last_name = data['lastName']
            email = data['email']
            password = data['password']
            existing_user = db_models.User.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'message': 'User already exists. Please login.'}), 400
            hashed_password = generate_password_hash(password)
            new_user = db_models.User(id=str(uuid.uuid4()), first_name=first_name, last_name=last_name, email=email, password=hashed_password)

            db.session.add(new_user)
            db.session.commit()

            return jsonify({'message': 'Successfully created user account'}), 200

        return jsonify({'message': 'Method not available for this route'}), 400


    @rest_bp.route("/rest/config", methods=['GET', 'POST'])
    @token_required
    def configRoute(current_user:db_models.User):
        if request.method == 'GET':
            configData = db_models.Config.query.filter_by(userId = current_user.id).first()
            if(configData):
                configDataJson = {
                    "videoHeight" : configData.videoHeight,
                    "videoWidth": configData.videoWidth,
                    "fps" : configData.fps,
                    "resolution" : configData.resolution,
                    "id" : configData.id
                    }
                return jsonify({"message": "Configuration found", "data": configDataJson})
            
            defaultStoredConfig = {
                "videoHeight": 480,
                "videoWidth": 640,
                "fps": 30
            }
            return jsonify({"message": "No configuration found with this id. Using default", "data": defaultStoredConfig})

        if request.method == 'POST':
            data = request.json
            videoHeight = data['videoHeight']
            videowidth = data['videoWidth']
            fps = data['fps']
            resolution = data['resolution']
            newConfigData = db_models.Config(id=str(uuid.uuid4()), userId = current_user.id, videoHeight=videoHeight, videowidth=videowidth, fps=fps, resolution = resolution)
            ets.setCameraDataFromConfig(newConfigData)
            db.session.add(newConfigData)
            db.session.commit()

            return jsonify({"message": "Created the config for the user successfully"})
        return jsonify({"message": "Unable to complete task"})


    @rest_bp.route("/rest/config/options", methods=['GET'])
    def configOptions():
        if request.method == 'GET':
            return

    return rest_bp





