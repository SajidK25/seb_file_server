from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db, User
from datetime import timedelta

auth_bp = Blueprint('auth', __name__, template_folder='templates/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Render login page and handle login logic."""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # Query user by email
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            # Create JWT token
            access_token = create_access_token(identity={
                'id': user.id,
                'username': user.username,
                'role': user.role
            }, expires_delta=timedelta(hours=1))

            # Set JWT token in cookies
            response = redirect(url_for('teachers.teacher_dashboard') if user.role == 'teacher' else url_for('students.student_portal'))
            set_access_cookies(response, access_token)

            flash('Login successful!', 'success')
            return response
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Render registration page and handle user registration."""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')  # 'teacher' or 'student'

        # Validate input
        if not username or not email or not password or not role:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))

        # Check if email is already registered
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Email is already registered.', 'danger')
            return redirect(url_for('auth.register'))

        # Hash the password and create a new user
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, email=email, password_hash=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('register.html')

@auth_bp.route('/logout', methods=['GET'])
def logout():
    """Handle logout by clearing JWT cookies."""
    response = redirect(url_for('auth.login'))
    unset_jwt_cookies(response)
    flash('You have been logged out.', 'success')
    return response