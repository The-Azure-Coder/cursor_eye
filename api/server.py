import uuid
from flask import Flask, render_template, request, redirect, url_for, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from extensions import db
from datetime import datetime, timezone, timedelta
from functools import wraps
import db_models
import helpers as JSONResponse
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'L4BAFopsgrhgGHaNAGpj4CUAY4LnnXAztrrgNwowRgAzADimnWDajZeTNPYaf7hV'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cursor_eye.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database setup
# -----------------------------
#  Create database tables
# -----------------------------
db.init_app(app)
with app.app_context():
    db.create_all()  # Creates all tables defined above if not existing



@app.route("/")
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
            data = jwt.decode(token_string, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = db_models.User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message': 'Token is invalid!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


@app.route("/auth/login",  methods=['POST'])
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
                           app.config['SECRET_KEY'], algorithm="HS256")

        return jsonify({"message": "Successfully logged in", "accessToken": token})

    return


@app.route("/auth/register", methods=['POST'])
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


@app.route("/config", methods=['GET', 'POST'])
@token_required
def configRoute(current_user:db_models.User):
    if request.method == 'GET':
        config = db_models.Config.query.filter_by(userId = current_user.id).first()
        if(config):
            return jsonify({"message": "Configuration found", "data": config})
        return jsonify({"message": "No configuration found with this id"})

    if request.method == 'POST':
        data = request.json

        return jsonify({"message": "Will work on this soon"})


@app.route("/config/options", methods=['GET'])
def configOptions():
    if request.method == 'GET':
        return


app.run()