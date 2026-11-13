"""
AI-Enhanced Admission Management System
Single-Command Local Launcher
Run: python run.py
"""

import os
import sys
import subprocess

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(PROJECT_ROOT, 'Backend')
ML_DIR = os.path.join(PROJECT_ROOT, 'ML')

sys.path.insert(0, BACKEND_DIR)

def verify_and_prepare():
    print("========================================================================")
    print("  AI-ENHANCED ADMISSION MANAGEMENT SYSTEM")
    print("  Initializing Institutional Admission Platform...")
    print("========================================================================")
    
    # 1. Verify ML Model
    model_file = os.path.join(BACKEND_DIR, 'admission_logistic_model.joblib')
    if not os.path.exists(model_file):
        print("[Setup] Training Machine Learning Logistic Regression model...")
        train_script = os.path.join(ML_DIR, 'train_model.py')
        subprocess.run([sys.executable, train_script], check=True)
        print("[Setup] ML model trained and synchronized.")
    else:
        print("[Setup] ML Model (Logistic Regression) is ready.")

    # 2. Verify Database
    db_file = os.path.join(BACKEND_DIR, 'admissions.db')
    if not os.path.exists(db_file):
        print("[Setup] Initializing and seeding database with initial data...")
        seed_script = os.path.join(BACKEND_DIR, 'seed_data.py')
        subprocess.run([sys.executable, seed_script], check=True)
        print("[Setup] Database populated.")
    else:
        print("[Setup] Database connection verified.")

    print("\n------------------------------------------------------------------------")
    print("  SYSTEM READY - STARTING LOCAL SERVER")
    print("------------------------------------------------------------------------")
    print("  Access Web Portal : http://127.0.0.1:5000")
    print("  Student Portal    : http://127.0.0.1:5000/student")
    print("  Admin Dashboard   : http://127.0.0.1:5000/admin")
    print("  Analytics Reports : http://127.0.0.1:5000/analytics")
    print("")
    print("  Default Credentials:")
    print("  Admin   : admin@institution.edu   | Password: Admin@123")
    print("  Student : student@institution.edu | Password: Student@123")
    print("========================================================================\n")

if __name__ == '__main__':
    verify_and_prepare()
    from app import create_app
    app = create_app()
    app.run(host='127.0.0.1', port=5000, debug=False)
