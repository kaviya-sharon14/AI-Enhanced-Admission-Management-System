"""
Machine Learning API Endpoints (Logistic Regression Inference and Evaluation Metrics)
"""

from flask import Blueprint, request, jsonify
from services.ml_service import ml_service
from database import get_db_connection
from auth_utils import login_required

ml_bp = Blueprint('ml_bp', __name__)

@ml_bp.route('/predict', methods=['POST'])
def predict_admission():
    data = request.get_json() or {}
    
    # Can predict for a specific application_id or raw values
    app_id = data.get('application_id')
    if app_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT academic_gpa, entrance_score, attendance_pct, prev_academic_score, category, extracurricular FROM applications WHERE id = ?", (app_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return jsonify({'success': False, 'message': 'Application not found'}), 404
        data = dict(row)
        
    try:
        result = ml_service.predict_eligibility(data)
        
        # If predicting for an application, optionally update database
        if app_id:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE applications 
            SET ml_prediction = ?, ml_probability = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """, (result['prediction'], result['probability'], app_id))
            conn.commit()
            conn.close()
            
        return jsonify({
            'success': True,
            'prediction': result['prediction'],
            'is_eligible': result['is_eligible'],
            'probability': result['probability'],
            'probability_percentage': result['probability_percentage'],
            'key_factors': result['key_factors'],
            'algorithm': result['algorithm'],
            'threshold': result['threshold']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Prediction error: {str(e)}'}), 500

@ml_bp.route('/metrics', methods=['GET'])
def get_metrics():
    metrics = ml_service.get_model_metrics()
    return jsonify({
        'success': True,
        'model_info': metrics
    })
