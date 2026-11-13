"""
Application Configuration
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)

# Automatically load .env if available
try:
    from dotenv import load_dotenv
    load_dotenv(os.path.join(PROJECT_ROOT, '.env'))
    load_dotenv(os.path.join(BASE_DIR, '.env'))
except ImportError:
    pass

SECRET_KEY = os.environ.get("SECRET_KEY", "institution-super-secure-key-2026-admission")
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024 # 16 MB limit

FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'Frontend')

# MongoDB Settings
# Supported formats:
# Local: "mongodb://localhost:27017/"
# MongoDB Atlas: "mongodb+srv://<username>:<password>@cluster0.mongodb.net/?retryWrites=true&w=majority"
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "admissions_db")
