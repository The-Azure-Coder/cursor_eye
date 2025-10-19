class Config:
    SECRET_KEY = 'L4BAFopsgrhgGHaNAGpj4CUAY4LnnXAztrrgNwowRgAzADimnWDajZeTNPYaf7hV'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cursor_eye.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

config = Config()