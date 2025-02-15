import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, File
from werkzeug.utils import secure_filename
from hashlib import sha256
from datetime import datetime
from config import Config

students_bp = Blueprint('students', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@students_bp.route('/files', methods=['GET'])
@jwt_required()
def student_portal():
    """Render the student portal with uploaded files."""
    current_user = get_jwt_identity()
    if current_user['role'] != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    # Query all files uploaded by the current student
    files = File.query.filter_by(user_id=current_user['id']).all()

    # Prepare data for the template
    file_list = [{
        'id': file.id,
        'filename': file.filename,
        'upload_date': file.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
        'is_approved': file.is_approved
    } for file in files]

    return render_template('student_portal.html', files=file_list)

@students_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_file():
    """Upload a file."""
    current_user = get_jwt_identity()
    if current_user['role'] != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    if 'file' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('students.student_portal'))

    file = request.files['file']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('students.student_portal'))

    if not allowed_file(file.filename):
        flash('File type not allowed', 'danger')
        return redirect(url_for('students.student_portal'))

    # Save the file securely
    filename = secure_filename(file.filename)
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)

    # Generate checksum for file integrity
    file_content = file.read()
    checksum = sha256(file_content).hexdigest()
    file.seek(0)  # Reset file pointer

    # Check if file with same checksum already exists
    existing_file = File.query.filter_by(checksum=checksum).first()
    if existing_file:
        flash('File already uploaded', 'danger')
        return redirect(url_for('students.student_portal'))

    file.save(filepath)

    # Save file metadata to database
    new_file = File(
        filename=filename,
        upload_date=datetime.utcnow(),
        user_id=current_user['id'],
        checksum=checksum
    )
    db.session.add(new_file)
    db.session.commit()

    flash('File uploaded successfully', 'success')
    return redirect(url_for('students.student_portal'))

@students_bp.route('/files/<int:file_id>/download', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """Download an approved file."""
    current_user = get_jwt_identity()
    if current_user['role'] != 'student':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    file = File.query.get(file_id)
    if not file or file.user_id != current_user['id']:
        flash('File not found', 'danger')
        return redirect(url_for('students.student_portal'))

    if not file.is_approved:
        flash('File not approved for download', 'danger')
        return redirect(url_for('students.student_portal'))

    return send_from_directory(Config.UPLOAD_FOLDER, file.filename, as_attachment=True)