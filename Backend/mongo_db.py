"""
MongoDB Integration Module for Admission Management System
Supports both Local MongoDB (e.g. mongodb://localhost:27017/) and MongoDB Atlas (Cloud).
Gracefully handles environments where pymongo or a live MongoDB instance is not yet running.
"""

import os
from datetime import datetime, timedelta
from config import MONGO_URI, MONGO_DB_NAME

# Global variables
_mongo_client = None
_mongo_db = None
_connection_checked = False
_connection_error = None

def get_mongo_client():
    """
    Initializes or returns cached PyMongo client.
    Returns None if pymongo is not installed or connection cannot be established.
    """
    global _mongo_client, _connection_checked, _connection_error
    if _mongo_client is not None:
        return _mongo_client

    try:
        import pymongo
    except ImportError:
        _connection_error = "PyMongo is not installed. Run: pip install pymongo"
        return None

    try:
        # 3 second timeout for initial connection test
        client = pymongo.MongoClient(
            MONGO_URI,
            serverSelectionTimeoutMS=3000,
            connectTimeoutMS=3000
        )
        # Verify connection by pinging
        client.admin.command('ping')
        _mongo_client = client
        _connection_error = None
        return _mongo_client
    except Exception as e:
        _connection_error = str(e)
        _mongo_client = None
        return None

def get_mongo_db():
    """Returns the MongoDB database object or None if unavailable."""
    global _mongo_db
    if _mongo_db is not None:
        return _mongo_db

    client = get_mongo_client()
    if client is not None:
        _mongo_db = client[MONGO_DB_NAME]
        init_mongo_indexes(_mongo_db)
        return _mongo_db
    return None

def is_mongo_connected() -> bool:
    """Checks whether MongoDB is connected and active."""
    return get_mongo_db() is not None

def init_mongo_indexes(db):
    """Ensures unique indexes for fast lookups and data integrity."""
    try:
        import pymongo
        db.users.create_index([("email", pymongo.ASCENDING)], unique=True)
        db.users.create_index([("id", pymongo.ASCENDING)])
        db.courses.create_index([("code", pymongo.ASCENDING)], unique=True)
        db.applications.create_index([("application_no", pymongo.ASCENDING)], unique=True)
        db.password_resets.create_index([("email", pymongo.ASCENDING)])
    except Exception:
        pass

def get_mongo_status() -> dict:
    """Returns detailed diagnostics about the MongoDB connection."""
    client = get_mongo_client()
    connected = client is not None
    
    # Mask credentials in URI for safe display
    safe_uri = MONGO_URI
    if "@" in safe_uri:
        prefix = safe_uri.split("@")[0]
        suffix = safe_uri.split("@")[1]
        protocol = prefix.split("://")[0]
        safe_uri = f"{protocol}://****:****@{suffix}"

    counts = {}
    if connected:
        db = get_mongo_db()
        try:
            counts = {
                'users': db.users.count_documents({}),
                'courses': db.courses.count_documents({}),
                'applications': db.applications.count_documents({}),
                'password_resets': db.password_resets.count_documents({})
            }
        except Exception:
            pass

    return {
        'connected': connected,
        'database': MONGO_DB_NAME,
        'uri': safe_uri,
        'error': _connection_error if not connected else None,
        'counts': counts
    }

# ==============================================================================
# User Management Operations
# ==============================================================================

def mongo_create_user(user_id: int, name: str, email: str, password_hash: str, role: str, phone: str = ""):
    """Creates a new user document in MongoDB."""
    db = get_mongo_db()
    if db is None:
        return False
    try:
        user_doc = {
            'id': user_id,
            'name': name,
            'email': email.lower().strip(),
            'password_hash': password_hash,
            'role': role,
            'phone': phone,
            'created_at': datetime.utcnow()
        }
        db.users.update_one({'email': email.lower().strip()}, {'$set': user_doc}, upsert=True)
        return True
    except Exception as e:
        print(f"[MongoDB] Error creating user: {e}")
        return False

def mongo_get_user_by_email(email: str):
    """Fetches user document by email from MongoDB."""
    db = get_mongo_db()
    if db is None:
        return None
    try:
        user = db.users.find_one({'email': email.lower().strip()})
        if user and '_id' in user:
            user['_id'] = str(user['_id'])
        return user
    except Exception as e:
        print(f"[MongoDB] Error finding user by email: {e}")
        return None

def mongo_get_user_by_id(user_id: int):
    """Fetches user document by ID from MongoDB."""
    db = get_mongo_db()
    if db is None:
        return None
    try:
        user = db.users.find_one({'id': int(user_id)})
        if user and '_id' in user:
            user['_id'] = str(user['_id'])
        return user
    except Exception as e:
        print(f"[MongoDB] Error finding user by ID: {e}")
        return None

def mongo_update_password(email: str, password_hash: str) -> bool:
    """Updates password hash for a user in MongoDB."""
    db = get_mongo_db()
    if db is None:
        return False
    try:
        result = db.users.update_one(
            {'email': email.lower().strip()},
            {'$set': {'password_hash': password_hash, 'updated_at': datetime.utcnow()}}
        )
        return result.modified_count > 0 or result.matched_count > 0
    except Exception as e:
        print(f"[MongoDB] Error updating password: {e}")
        return False

# ==============================================================================
# Password Reset Operations
# ==============================================================================

def mongo_save_reset_code(email: str, code: str, expires_in_minutes: int = 15):
    """Stores password reset verification code in MongoDB."""
    db = get_mongo_db()
    if db is None:
        return False
    try:
        # Invalidate previous unused codes for this email
        db.password_resets.update_many(
            {'email': email.lower().strip(), 'used': False},
            {'$set': {'used': True}}
        )
        
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        db.password_resets.insert_one({
            'email': email.lower().strip(),
            'reset_code': str(code).strip(),
            'expires_at': expires_at,
            'used': False,
            'created_at': datetime.utcnow()
        })
        return True
    except Exception as e:
        print(f"[MongoDB] Error saving reset code: {e}")
        return False

def mongo_verify_and_use_reset_code(email: str, code: str) -> bool:
    """Verifies reset code and marks it as used if valid and not expired."""
    db = get_mongo_db()
    if db is None:
        return False
    try:
        now = datetime.utcnow()
        doc = db.password_resets.find_one({
            'email': email.lower().strip(),
            'reset_code': str(code).strip(),
            'used': False,
            'expires_at': {'$gt': now}
        })
        if doc:
            db.password_resets.update_one({'_id': doc['_id']}, {'$set': {'used': True}})
            return True
        return False
    except Exception as e:
        print(f"[MongoDB] Error verifying reset code: {e}")
        return False

# ==============================================================================
# SQLite to MongoDB Data Synchronization
# ==============================================================================

def sync_sqlite_to_mongo():
    """
    Synchronizes users, courses, and applications from SQLite to MongoDB.
    Ensures seamless transition when MongoDB is enabled.
    """
    db = get_mongo_db()
    if db is None:
        return {'success': False, 'message': 'MongoDB is not connected.'}

    from database import get_db_connection
    conn = get_db_connection()
    cursor = conn.cursor()

    synced = {'users': 0, 'courses': 0, 'applications': 0}

    # 1. Sync Users
    cursor.execute("SELECT id, name, email, password_hash, role, phone, created_at FROM users")
    users = cursor.fetchall()
    for u in users:
        db.users.update_one(
            {'email': u['email']},
            {'$set': {
                'id': u['id'],
                'name': u['name'],
                'email': u['email'],
                'password_hash': u['password_hash'],
                'role': u['role'],
                'phone': u['phone'],
                'created_at': u['created_at']
            }},
            upsert=True
        )
        synced['users'] += 1

    # 2. Sync Courses
    cursor.execute("SELECT code, name, department, seats, min_gpa, min_entrance FROM courses")
    courses = cursor.fetchall()
    for c in courses:
        db.courses.update_one(
            {'code': c['code']},
            {'$set': dict(c)},
            upsert=True
        )
        synced['courses'] += 1

    # 3. Sync Applications
    cursor.execute("SELECT * FROM applications")
    apps = cursor.fetchall()
    for a in apps:
        app_dict = dict(a)
        db.applications.update_one(
            {'application_no': app_dict['application_no']},
            {'$set': app_dict},
            upsert=True
        )
        synced['applications'] += 1

    conn.close()
    return {
        'success': True,
        'message': f"Synchronized {synced['users']} users, {synced['courses']} courses, {synced['applications']} applications to MongoDB.",
        'synced': synced
    }

