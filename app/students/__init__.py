from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import db, File
from werkzeug.utils import secure_filename
from hashlib import sha256
from datetime import datetime
import os

students_bp = Blueprint('students', __name__)

# Allowed file extensions for upload
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'jpg', 'png'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@students_bp.route('/student_portal', methods=['GET'])
@login_required
def student_portal():
    """Render the student portal with uploaded files."""
    if current_user.role != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    # Query all files uploaded by the current student
    files = File.query.filter_by(user_id=current_user.id).all()

    # Prepare data for the template
    file_list = [{
        'id': file.id,
        'filename': file.filename,
        'upload_date': file.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
        'is_approved': file.is_approved
    } for file in files]

    return render_template('student_portal.html', files=file_list)

@students_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload from the student portal."""
    if current_user.role != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    # Check if the request has a file part
    if 'file' not in request.files:
        flash('No file part in the request.', 'danger')
        return redirect(url_for('students.student_portal'))

    file = request.files['file']

    # Check if the file is selected
    if file.filename == '':
        flash('No file selected for upload.', 'danger')
        return redirect(url_for('students.student_portal'))

    # Validate file type
    if not allowed_file(file.filename):
        flash('Invalid file type. Allowed types are: pdf, docx, txt, jpg, png.', 'danger')
        return redirect(url_for('students.student_portal'))

    # Validate file size (e.g., max 5MB)
    file.seek(0, os.SEEK_END)  # Move to the end of the file
    file_length = file.tell()  # Get the file size
    max_file_size = 5 * 1024 * 1024  # 5MB in bytes
    if file_length > max_file_size:
        flash('File size exceeds the 5MB limit.', 'danger')
        return redirect(url_for('students.student_portal'))
    file.seek(0)  # Reset the file pointer after size check

    # Save the file
    filename = secure_filename(file.filename)
    upload_folder = current_app.config.get('UPLOAD_FOLDER', 'uploads')
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    # Generate a unique filename using SHA256
    unique_filename = sha256((filename + str(datetime.now())).encode()).hexdigest()[:20] + os.path.splitext(filename)[1]
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)

    # Save file details in the database
    new_file = File(
        filename=filename,
        user_id=current_user.id,
        upload_date=datetime.now(),
        is_approved=False  # Default to not approved
    )
    db.session.add(new_file)
    db.session.commit()

    flash('File uploaded successfully and is pending approval.', 'success')
    return redirect(url_for('students.student_portal'))