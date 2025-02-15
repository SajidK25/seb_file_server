
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # 'teacher'/'student'
    password_hash = db.Column(db.String(128), nullable=False)
    files = db.relationship('File', backref='owner', lazy=True)

    # Flask-Login attributes
    @property
    def is_active(self):
        """Return True if the user account is active."""
        return True  # Set to False if you implement account deactivation

    @property
    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return True

    @property
    def is_anonymous(self):
        """Return False for authenticated users."""
        return False

    def get_id(self):
        """Return the unique identifier for the user."""
        return str(self.id)
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    checksum = db.Column(db.String(64), unique=True)
    is_approved = db.Column(db.Boolean, default=False)  # Teacher approval status