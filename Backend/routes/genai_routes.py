"""
Generative AI API Endpoints (Evaluation & Recommendation Report Generator)
"""

from flask import Blueprint, request, jsonify, g
from database import get_db_connection
from auth_utils import login_required, admin_required
from services.genai_service import genai_service
from services.ml_service import ml_service

genai_bp = Blueprint('genai_bp', __name__)

@genai_bp.route('/evaluate/<int:app_id>', methods=['POST'])
@login_required
def evaluate_application(app_id):
    data = request.get_json() or {}
    custom_instructions = data.get('instructions', '').strip()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT a.*, c.name as course_name 
    FROM applications a
    LEFT JOIN courses c ON a.course_code = c.code
    WHERE a.id = ?
    """, (app_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return jsonify({'success': False, 'message': 'Application not found'}), 404
        
    app_data = dict(row)
    
    # 1. Run ML Prediction for up-to-date probabilistic score
    ml_input = {
        'academic_gpa': app_data['academic_gpa'],
        'entrance_score': app_data['entrance_score'],
        'attendance_pct': app_data['attendance_pct'],
        'prev_academic_score': app_data['prev_academic_score'],
        'category': app_data['category'],
        'extracurricular': app_data['extracurricular']
    }
    ml_res = ml_service.predict_eligibility(ml_input)
    
    # 2. Run GenAI Evaluation
    applicant_profile = {
        'full_name': app_data['full_name'],
        'course_name': app_data['course_name'],
        'course_code': app_data['course_code'],
        'academic_gpa': app_data['academic_gpa'],
        'entrance_score': app_data['entrance_score'],
        'attendance_pct': app_data['attendance_pct'],
        'prev_academic_score': app_data['prev_academic_score'],
        'category': app_data['category'],
        'extracurricular': app_data['extracurricular']
    }
    
    ai_report = genai_service.generate_evaluation_report(
        applicant=applicant_profile,
        ml_result=ml_res,
        custom_instructions=custom_instructions
    )
    
    # 3. Update application in database with newly generated report
    cursor.execute("""
    UPDATE applications 
    SET ai_evaluation_summary = ?,
        ai_recommendation = ?,
        ai_profile_insights = ?,
        ai_explanation = ?,
        ml_prediction = ?,
        ml_probability = ?,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (
        ai_report['evaluation_summary'],
        ai_report['admission_recommendation'],
        ai_report['profile_insights'],
        ai_report['approval_rejection_explanation'],
        ml_res['prediction'],
        ml_res['probability'],
        app_id
    ))
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': 'AI Evaluation and Recommendation Report generated successfully.',
        'report': ai_report,
        'ml_prediction': ml_res
    })

@genai_bp.route('/generate', methods=['POST'])
def generate_adhoc_report():
    data = request.get_json() or {}
    try:
        ml_res = ml_service.predict_eligibility(data)
        ai_report = genai_service.generate_evaluation_report(
            applicant=data,
            ml_result=ml_res,
            custom_instructions=data.get('instructions')
        )
        return jsonify({
            'success': True,
            'report': ai_report,
            'ml_prediction': ml_res
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
