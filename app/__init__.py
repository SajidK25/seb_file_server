from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from app.auth import auth_bp
from app.teachers import teachers_bp
from app.students import students_bp
from app.models import db
from app.models import User


# db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
login_manager = LoginManager()

# Specify the login view for unauthorized access
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri="redis://localhost:6379/0"
    )

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)
    login_manager.init_app(app)

    # Register blueprints

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(teachers_bp, url_prefix='/teachers')
    app.register_blueprint(students_bp, url_prefix='/students')

    return app