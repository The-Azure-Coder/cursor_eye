from extensions import db
from sqlalchemy import ForeignKey

class Config( db.Model):
    __tablename__ = 'configs'
    id = db.Column(db.String, primary_key=True)
    resolution = db.Column(db.String(50), unique=True)
    fps = db.Column(db.String(100))
    videoWidth = db.Column(db.String(70), unique=True)
    videoHeight = db.Column(db.String(80))
    userId = db.Column(db.String(100),ForeignKey("users.id"))


class User(db.Model):
    __tablename__ = 'users'  # optional custom table name
    id = db.Column(db.String(100), primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(70), unique=True)
    password = db.Column(db.String(80))

    def to_dict(self):
        """Convert model instance to dictionary (for JSON responses)"""
        return {
            "id": self.id,
            "firstName": self.first_name,
            "lastName": self.last_name,
            "email": self.email
        }