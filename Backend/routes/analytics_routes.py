"""
Reports and Analytics API Endpoints
"""

import io
import csv
from flask import Blueprint, jsonify, Response
from database import get_db_connection
from auth_utils import admin_required

analytics_bp = Blueprint('analytics_bp', __name__)

@analytics_bp.route('/summary', methods=['GET'])
def get_analytics_summary():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Total & Status counts
    cursor.execute("""
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END) as approved,
        SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) as rejected,
        SUM(CASE WHEN status = 'Under Review' THEN 1 ELSE 0 END) as under_review,
        SUM(CASE WHEN status = 'Submitted' THEN 1 ELSE 0 END) as pending,
        SUM(CASE WHEN status = 'Waitlisted' THEN 1 ELSE 0 END) as waitlisted,
        AVG(academic_gpa) as avg_gpa,
        AVG(entrance_score) as avg_entrance,
        AVG(attendance_pct) as avg_attendance,
        SUM(CASE WHEN ml_prediction = 'Eligible for Admission' THEN 1 ELSE 0 END) as ml_eligible_count
    FROM applications
    """)
    stats = dict(cursor.fetchone())
    
    # Calculations
    total = stats['total'] or 0
    approved = stats['approved'] or 0
    acceptance_rate = round((approved / total * 100), 2) if total > 0 else 0.0
    ml_eligible_pct = round(((stats['ml_eligible_count'] or 0) / total * 100), 2) if total > 0 else 0.0
    
    # 2. Applications by Course
    cursor.execute("""
    SELECT c.code, c.name, COUNT(a.id) as count,
           SUM(CASE WHEN a.status = 'Approved' THEN 1 ELSE 0 END) as approved_count
    FROM courses c
    LEFT JOIN applications a ON c.code = a.course_code
    GROUP BY c.code, c.name
    ORDER BY count DESC
    """)
    course_stats = [dict(row) for row in cursor.fetchall()]
    
    # 3. Status Breakdown
    cursor.execute("""
    SELECT status, COUNT(*) as count 
    FROM applications 
    GROUP BY status
    """)
    status_stats = [dict(row) for row in cursor.fetchall()]
    
    # 4. Category Breakdown
    cursor.execute("""
    SELECT category, COUNT(*) as count,
           AVG(academic_gpa) as avg_gpa,
           AVG(entrance_score) as avg_entrance
    FROM applications
    GROUP BY category
    """)
    category_stats = [dict(row) for row in cursor.fetchall()]
    
    # 5. Extracurricular Breakdown
    cursor.execute("""
    SELECT extracurricular, COUNT(*) as count 
    FROM applications 
    GROUP BY extracurricular
    """)
    ec_stats = [dict(row) for row in cursor.fetchall()]

    conn.close()
    
    return jsonify({
        'success': True,
        'summary': {
            'total_applications': total,
            'approved': approved,
            'rejected': stats['rejected'] or 0,
            'under_review': stats['under_review'] or 0,
            'pending': stats['pending'] or 0,
            'waitlisted': stats['waitlisted'] or 0,
            'acceptance_rate': acceptance_rate,
            'avg_gpa': round(stats['avg_gpa'] or 0, 2),
            'avg_entrance_score': round(stats['avg_entrance'] or 0, 2),
            'avg_attendance': round(stats['avg_attendance'] or 0, 2),
            'ml_eligible_rate': ml_eligible_pct
        },
        'courses': course_stats,
        'status_breakdown': status_stats,
        'category_stats': category_stats,
        'extracurricular_stats': ec_stats
    })

@analytics_bp.route('/export-csv', methods=['GET'])
def export_applications_csv():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.application_no, a.full_name, a.email, a.phone, a.dob, a.gender,
           c.name as course_name, a.academic_gpa, a.entrance_score, a.attendance_pct,
           a.prev_academic_score, a.category, a.extracurricular, a.status,
           a.ml_prediction, a.ml_probability, a.admin_remarks, a.submitted_at
    FROM applications a
    LEFT JOIN courses c ON a.course_code = c.code
    ORDER BY a.submitted_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow([
        'Application Number', 'Applicant Name', 'Email', 'Phone', 'Date of Birth', 'Gender',
        'Course', 'Academic GPA (%)', 'Entrance Score', 'Attendance (%)',
        'Previous Board Score (%)', 'Category', 'Extracurriculars', 'Admission Status',
        'ML Prediction', 'ML Probability', 'Admin Remarks', 'Submission Timestamp'
    ])
    
    for row in rows:
        writer.writerow(list(row))
        
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=institutional_admissions_report_2026.csv"}
    )
