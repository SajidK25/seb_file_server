from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, User, File

teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('/teacher_dashboard', methods=['GET'])
@login_required
def teacher_dashboard():
    """Render the teacher dashboard with uploaded files and student activity."""
    if current_user.role != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    # Query all uploaded files
    files = File.query.all()

    # Query all students
    students = User.query.filter_by(role='student').all()

    # Prepare data for the template
    file_list = [{
        'id': file.id,
        'filename': file.filename,
        'upload_date': file.upload_date.strftime('%Y-%m-%d %H:%M:%S'),
        'owner': User.query.get(file.user_id).username,
        'is_approved': file.is_approved
    } for file in files]

    student_list = [{
        'id': student.id,
        'username': student.username,
        'uploaded_files': len(student.files)
    } for student in students]

    return render_template('teacher_dashboard.html', files=file_list, students=student_list)
