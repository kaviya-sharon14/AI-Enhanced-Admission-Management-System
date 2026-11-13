"""
Application Management API Endpoints (Submission, Status Tracking, Admin Review Workflow)
"""

import os
import time
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, g, send_from_directory, current_app
from database import get_db_connection
from auth_utils import login_required, admin_required
from config import UPLOAD_FOLDER, ALLOWED_EXTENSIONS
from services.ml_service import ml_service
from services.genai_service import genai_service

app_bp = Blueprint('app_bp', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app_bp.route('/apply', methods=['POST'])
@login_required
def submit_application():
    user = g.current_user
    user_id = user['sub']
    
    # Handle Multipart Form Data or JSON
    if request.content_type and 'multipart/form-data' in request.content_type:
        form = request.form
        files = request.files
    else:
        form = request.get_json() or {}
        files = {}
        
    full_name = form.get('full_name', user.get('name', '')).strip()
    email = form.get('email', user.get('email', '')).strip()
    phone = form.get('phone', '').strip()
    dob = form.get('dob', '').strip()
    gender = form.get('gender', 'Other').strip()
    address = form.get('address', '').strip()
    course_code = form.get('course_code', '').strip()
    
    try:
        academic_gpa = float(form.get('academic_gpa', 0))
        entrance_score = float(form.get('entrance_score', 0))
        attendance_pct = float(form.get('attendance_pct', 0))
        prev_academic_score = float(form.get('prev_academic_score', 0))
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Academic scores must be valid numbers.'}), 400
        
    category = form.get('category', 'General').strip()
    extracurricular = form.get('extracurricular', 'None').strip()
    
    if not full_name or not email or not course_code:
        return jsonify({'success': False, 'message': 'Full name, email, and course selection are mandatory.'}), 400
        
    # File upload handling
    document_path = None
    document_name = None
    if 'document' in files:
        file = files['document']
        if file and file.filename != '' and allowed_file(file.filename):
            orig_filename = secure_filename(file.filename)
            timestamp = int(time.time())
            unique_filename = f"user_{user_id}_{timestamp}_{orig_filename}"
            save_path = os.path.join(UPLOAD_FOLDER, unique_filename)
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            file.save(save_path)
            document_path = save_path
            document_name = orig_filename
            
    # Auto-generate Unique Application Number
    timestamp_suffix = str(int(time.time()))[-4:]
    app_no = f"ADM-2026-{timestamp_suffix}{user_id:02d}"
    
    # Fetch course name
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM courses WHERE code = ?", (course_code,))
    course_row = cursor.fetchone()
    course_name = course_row['name'] if course_row else course_code
    
    # 1. Execute ML Eligibility Prediction
    ml_input = {
        'academic_gpa': academic_gpa,
        'entrance_score': entrance_score,
        'attendance_pct': attendance_pct,
        'prev_academic_score': prev_academic_score,
        'category': category,
        'extracurricular': extracurricular
    }
    ml_result = ml_service.predict_eligibility(ml_input)
    
    # 2. Execute Generative AI Report Synthesis
    applicant_profile = {
        'full_name': full_name,
        'course_name': course_name,
        'course_code': course_code,
        'academic_gpa': academic_gpa,
        'entrance_score': entrance_score,
        'attendance_pct': attendance_pct,
        'prev_academic_score': prev_academic_score,
        'category': category,
        'extracurricular': extracurricular
    }
    ai_report = genai_service.generate_evaluation_report(applicant_profile, ml_result)
    
    # 3. Store Application
    cursor.execute("""
    INSERT INTO applications (
        application_no, user_id, full_name, email, phone, dob, gender, address,
        course_code, academic_gpa, entrance_score, attendance_pct, prev_academic_score,
        category, extracurricular, document_path, document_name, status,
        ml_prediction, ml_probability,
        ai_evaluation_summary, ai_recommendation, ai_profile_insights, ai_explanation
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Submitted', ?, ?, ?, ?, ?, ?)
    """, (
        app_no, user_id, full_name, email, phone, dob, gender, address,
        course_code, academic_gpa, entrance_score, attendance_pct, prev_academic_score,
        category, extracurricular, document_path, document_name,
        ml_result['prediction'], ml_result['probability'],
        ai_report['evaluation_summary'], ai_report['admission_recommendation'],
        ai_report['profile_insights'], ai_report['approval_rejection_explanation']
    ))
    conn.commit()
    app_id = cursor.lastrowid
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'Application submitted successfully with AI & ML evaluation.',
        'application_no': app_no,
        'application_id': app_id,
        'ml_prediction': ml_result['prediction'],
        'ml_probability': ml_result['probability_percentage'],
        'ai_evaluation_summary': ai_report['evaluation_summary']
    }), 201

@app_bp.route('/my', methods=['GET'])
@login_required
def get_my_applications():
    user_id = g.current_user['sub']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.*, c.name as course_name, c.department 
    FROM applications a
    LEFT JOIN courses c ON a.course_code = c.code
    WHERE a.user_id = ?
    ORDER BY a.submitted_at DESC
    """, (user_id,))
    apps = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'success': True,
        'applications': apps
    })

@app_bp.route('', methods=['GET'])
@admin_required
def get_all_applications():
    status = request.args.get('status')
    course = request.args.get('course')
    search = request.args.get('search')
    
    query = """
    SELECT a.*, c.name as course_name, c.department 
    FROM applications a
    LEFT JOIN courses c ON a.course_code = c.code
    WHERE 1=1
    """
    params = []
    
    if status and status != 'All':
        query += " AND a.status = ?"
        params.append(status)
        
    if course and course != 'All':
        query += " AND a.course_code = ?"
        params.append(course)
        
    if search:
        query += " AND (a.full_name LIKE ? OR a.application_no LIKE ? OR a.email LIKE ?)"
        like_search = f"%{search}%"
        params.extend([like_search, like_search, like_search])
        
    query += " ORDER BY a.submitted_at DESC"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query, params)
    applications = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return jsonify({
        'success': True,
        'total': len(applications),
        'applications': applications
    })

@app_bp.route('/<int:app_id>', methods=['GET'])
@login_required
def get_application_detail(app_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.*, c.name as course_name, c.department, c.min_gpa, c.min_entrance
    FROM applications a
    LEFT JOIN courses c ON a.course_code = c.code
    WHERE a.id = ?
    """, (app_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return jsonify({'success': False, 'message': 'Application not found.'}), 404
        
    app_data = dict(row)
    # Check permissions: student can only view their own
    if g.current_user['role'] != 'admin' and app_data['user_id'] != g.current_user['sub']:
        return jsonify({'success': False, 'message': 'Unauthorized to view this application.'}), 403
        
    return jsonify({
        'success': True,
        'application': app_data
    })

@app_bp.route('/<int:app_id>/status', methods=['PUT'])
@admin_required
def update_application_status(app_id):
    data = request.get_json() or {}
    new_status = data.get('status')
    remarks = data.get('remarks', '').strip()
    reviewer_name = g.current_user.get('name', 'Admission Officer')
    
    valid_statuses = ['Submitted', 'Under Review', 'Approved', 'Rejected', 'Waitlisted']
    if new_status not in valid_statuses:
        return jsonify({'success': False, 'message': f'Invalid status. Allowed values: {valid_statuses}'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE applications 
    SET status = ?, admin_remarks = ?, reviewed_by = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (new_status, remarks, reviewer_name, app_id))
    conn.commit()
    rows_affected = cursor.rowcount
    conn.close()
    
    if rows_affected == 0:
        return jsonify({'success': False, 'message': 'Application record not found.'}), 404
        
    return jsonify({
        'success': True,
        'message': f'Application status updated to {new_status} successfully.',
        'status': new_status,
        'remarks': remarks,
        'reviewed_by': reviewer_name
    })

@app_bp.route('/document/<filename>', methods=['GET'])
def get_uploaded_document(filename):
    safe_name = secure_filename(filename)
    if not os.path.exists(os.path.join(UPLOAD_FOLDER, safe_name)):
        return jsonify({'success': False, 'message': 'Document file not found.'}), 404
    return send_from_directory(UPLOAD_FOLDER, safe_name)
