from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    """Connect to database"""
    db.app = app
    db.init_app(app)

class Workout(db.Model):
    __tablename__ = "workout"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    exercise = db.Column(db.Text, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False, default=10)
    sets = db.Column(db.Integer, nullable=False, default=3)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref="workout")

class Nutrition(db.Model):
    __tablename__ = "nutrition"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    food = db.Column(db.Text, nullable=False)
    protein = db.Column(db.Integer, nullable=False)
    carbs = db.Column(db.Integer, nullable=False)
    fats = db.Column(db.Integer, nullable=False)
    calories = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship('User', backref="nutrition")

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    profile_image = db.Column(db.String(120), default='default.jpg')  # Added profile image field

    # other columns and methods...

    @classmethod
    def register(cls, username, password):
        """Register user with hashed pwd and return user"""

        hashed = bcrypt.generate_password_hash(password)

        # turn bytestring into normal unicode utf8 string
        hashed_utf8 = hashed.decode("utf8")

        # return instance of user with username and hashed pwd
        return cls(username=username, password=hashed_utf8)

    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists and password is correct
        
        Return user if valid; else return False
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            # return user instance

            return u
        else:
            return False

