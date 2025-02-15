from flask import Blueprint, request, jsonify
from app.models import db, User
from flask_jwt_extended import create_access_token
from datetime import timedelta

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'User already exists'}), 400

    user = User(username=data['username'], role=data.get('role', 'student'))
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(username=data['username']).first()

    if user and user.check_password(data['password']):
        token = create_access_token(identity={'id': user.id, 'role': user.role}, expires_delta=timedelta(minutes=30))
        return jsonify({'token': token}), 200

    return jsonify({'message': 'Invalid credentials'}), 401