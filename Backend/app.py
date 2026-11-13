"""
Flask Application Entry Point for AI-Enhanced Admission Management System
Serves both REST APIs and Frontend web portal with zero configuration needed.
"""

import os
from flask import Flask, send_from_directory, jsonify
from config import FRONTEND_DIR, UPLOAD_FOLDER
from database import init_db
from routes.auth_routes import auth_bp
from routes.application_routes import app_bp
from routes.ml_routes import ml_bp
from routes.genai_routes import genai_bp
from routes.analytics_routes import analytics_bp

def create_app():
    app = Flask(__name__, static_folder=None)
    
    # Initialize DB schema
    init_db()
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Register API Blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(app_bp, url_prefix='/api/applications')
    app.register_blueprint(ml_bp, url_prefix='/api/ml')
    app.register_blueprint(genai_bp, url_prefix='/api/genai')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Static Assets & Frontend Routing
    @app.route('/')
    def serve_index():
        return send_from_directory(FRONTEND_DIR, 'index.html')
        
    @app.route('/login')
    def serve_login():
        return send_from_directory(FRONTEND_DIR, 'login.html')
        
    @app.route('/student')
    def serve_student():
        return send_from_directory(FRONTEND_DIR, 'student.html')
        
    @app.route('/admin')
    def serve_admin():
        return send_from_directory(FRONTEND_DIR, 'admin.html')
        
    @app.route('/analytics')
    def serve_analytics():
        return send_from_directory(FRONTEND_DIR, 'analytics.html')
        
    @app.route('/css/<path:filename>')
    def serve_css(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'css'), filename)
        
    @app.route('/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory(os.path.join(FRONTEND_DIR, 'js'), filename)
        
    @app.route('/uploads/<path:filename>')
    def serve_uploads(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)
        
    @app.route('/api/health')
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'AI-Enhanced Admission Management System',
            'version': '1.0.0',
            'ml_model': 'Logistic Regression (Active)',
            'genai_engine': 'Ready'
        })
        
    # Global CORS header hook
    @app.after_request
    def add_cors_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        return response

    return app

if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    print("=================================================================")
    print("AI-ENHANCED ADMISSION MANAGEMENT SYSTEM")
    print(f"Portal running locally at: http://127.0.0.1:{port}")
    print("Admin credentials : admin@institution.edu / Admin@123")
    print("Student credentials: student@institution.edu / Student@123")
    print("=================================================================")
    app.run(host='0.0.0.0', port=port, debug=True)
