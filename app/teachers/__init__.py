from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import db, User, File

teachers_bp = Blueprint('teachers', __name__)

@teachers_bp.route('/files', methods=['GET'])
@jwt_required()
def teacher_dashboard():
    """Render the teacher dashboard with uploaded files and student activity."""
    current_user = get_jwt_identity()
    if current_user['role'] != 'teacher':
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

@teachers_bp.route('/files/<int:file_id>/approve', methods=['POST'])
@jwt_required()
def approve_file(file_id):
    """Approve a file uploaded by a student."""
    current_user = get_jwt_identity()
    if current_user['role'] != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    file = File.query.get(file_id)
    if not file:
        flash('File not found', 'danger')
        return redirect(url_for('teachers.teacher_dashboard'))

    file.is_approved = True
    db.session.commit()
    flash(f'File "{file.filename}" approved successfully.', 'success')
    return redirect(url_for('teachers.teacher_dashboard'))

@teachers_bp.route('/files/<int:file_id>', methods=['POST'])
@jwt_required()
def delete_file(file_id):
    """Delete a file."""
    current_user = get_jwt_identity()
    if current_user['role'] != 'teacher':
        flash('Access denied', 'danger')
        return redirect(url_for('auth.login'))

    file = File.query.get(file_id)
    if not file:
        flash('File not found', 'danger')
        return redirect(url_for('teachers.teacher_dashboard'))

    db.session.delete(file)
    db.session.commit()
    flash(f'File "{file.filename}" deleted successfully.', 'success')
    return redirect(url_for('teachers.teacher_dashboard'))