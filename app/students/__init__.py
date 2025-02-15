from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, File
from werkzeug.utils import secure_filename
from hashlib import sha256
from datetime import datetime
from config import Config

students_bp = Blueprint('students', __name__)

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
