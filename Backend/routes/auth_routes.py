"""
Authentication API Endpoints (Student & Admin Login / Registration, Forgot Password, and MongoDB Sync)
"""

import secrets
from flask import Blueprint, request, jsonify, g
from database import (
    get_db_connection,
    hash_password,
    save_sqlite_reset_code,
    verify_and_use_sqlite_reset_code,
    update_sqlite_user_password
)
from auth_utils import generate_jwt, login_required
from mongo_db import (
    is_mongo_connected,
    mongo_create_user,
    mongo_get_user_by_email,
    mongo_update_password,
    mongo_save_reset_code,
    mongo_verify_and_use_reset_code,
    sync_sqlite_to_mongo,
    get_mongo_status
)

auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    phone = data.get('phone', '').strip()
    role = data.get('role', 'student').strip()
    
    if not name or not email or not password:
        return jsonify({'success': False, 'message': 'Name, email, and password are required.'}), 400
        
    if len(password) < 6:
        return jsonify({'success': False, 'message': 'Password must be at least 6 characters long.'}), 400

    if role not in ['student', 'admin']:
        role = 'student'
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check existing email in SQLite
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return jsonify({'success': False, 'message': 'An account with this email address already exists.'}), 409
        
    pw_hash = hash_password(password)
    cursor.execute("""
    INSERT INTO users (name, email, password_hash, role, phone)
    VALUES (?, ?, ?, ?, ?)
    """, (name, email, pw_hash, role, phone))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    
    # Also sync/save into MongoDB if connected
    if is_mongo_connected():
        mongo_create_user(user_id, name, email, pw_hash, role, phone)
    
    token = generate_jwt(user_id, email, role, name)
    return jsonify({
        'success': True,
        'message': 'Account registered successfully.',
        'token': token,
        'user': {
            'id': user_id,
            'name': name,
            'email': email,
            'role': role,
            'phone': phone
        }
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    
    if not email or not password:
        return jsonify({'success': False, 'message': 'Email and password are required.'}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, password_hash, role, phone FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    expected_hash = hash_password(password)
    
    if not user:
        # Check MongoDB if connected in case user was registered directly there
        if is_mongo_connected():
            m_user = mongo_get_user_by_email(email)
            if m_user and m_user.get('password_hash') == expected_hash:
                user = m_user
            else:
                return jsonify({'success': False, 'message': 'Invalid credentials. User not found.'}), 401
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials. User not found.'}), 401
    else:
        if user['password_hash'] != expected_hash:
            return jsonify({'success': False, 'message': 'Invalid credentials. Incorrect password.'}), 401
        # Keep MongoDB in sync
        if is_mongo_connected():
            mongo_create_user(user['id'], user['name'], user['email'], user['password_hash'], user['role'], user['phone'])
        
    user_id = user['id']
    user_email = user['email']
    user_role = user['role']
    user_name = user['name']
    user_phone = user['phone'] if 'phone' in user else ''
    
    token = generate_jwt(user_id, user_email, user_role, user_name)
    return jsonify({
        'success': True,
        'message': 'Logged in successfully.',
        'token': token,
        'user': {
            'id': user_id,
            'name': user_name,
            'email': user_email,
            'role': user_role,
            'phone': user_phone
        }
    })

@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """
    Generates a 6-digit reset code for a registered user's email.
    Saves in SQLite and MongoDB, and returns code for instant UI confirmation.
    """
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({'success': False, 'message': 'Email address is required.'}), 400
        
    # Check if user exists in SQLite
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user and is_mongo_connected():
        user = mongo_get_user_by_email(email)
        
    if not user:
        return jsonify({'success': False, 'message': 'No registered account found with this email address.'}), 404
        
    # Generate 6-digit verification code
    reset_code = f"{secrets.randbelow(900000) + 100000}"
    
    # Save to SQLite
    save_sqlite_reset_code(email, reset_code, expires_in_minutes=15)
    
    # Save to MongoDB if connected
    if is_mongo_connected():
        mongo_save_reset_code(email, reset_code, expires_in_minutes=15)
        
    return jsonify({
        'success': True,
        'message': f'Verification code generated successfully for {email}.',
        'email': email,
        'reset_code': reset_code,
        'expires_in_minutes': 15
    })

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """
    Validates the 6-digit reset code and sets a new password.
    Updates SQLite and MongoDB.
    """
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    reset_code = str(data.get('reset_code', '')).strip()
    new_password = data.get('new_password', '').strip()
    
    if not email or not reset_code or not new_password:
        return jsonify({'success': False, 'message': 'Email, reset code, and new password are required.'}), 400
        
    if len(new_password) < 6:
        return jsonify({'success': False, 'message': 'New password must be at least 6 characters long.'}), 400
        
    # Verify code in SQLite or MongoDB
    sqlite_valid = verify_and_use_sqlite_reset_code(email, reset_code)
    mongo_valid = False
    if is_mongo_connected():
        mongo_valid = mongo_verify_and_use_reset_code(email, reset_code)
        
    if not sqlite_valid and not mongo_valid:
        return jsonify({
            'success': False,
            'message': 'Invalid or expired verification code. Please request a new code.'
        }), 400
        
    # Hash the new password
    new_pw_hash = hash_password(new_password)
    
    # Update in SQLite
    update_sqlite_user_password(email, new_pw_hash)
    
    # Update in MongoDB if connected
    if is_mongo_connected():
        mongo_update_password(email, new_pw_hash)
        
    return jsonify({
        'success': True,
        'message': 'Password has been reset successfully! You can now log in with your new password.'
    })

@auth_bp.route('/db-status', methods=['GET'])
def db_status():
    """Returns database connection status for MongoDB and SQLite."""
    mongo_stat = get_mongo_status()
    
    # SQLite counts
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS count FROM users")
    user_count = cursor.fetchone()['count']
    cursor.execute("SELECT COUNT(*) AS count FROM applications")
    app_count = cursor.fetchone()['count']
    conn.close()
    
    return jsonify({
        'success': True,
        'mongodb': mongo_stat,
        'sqlite': {
            'connected': True,
            'file': 'admissions.db',
            'counts': {
                'users': user_count,
                'applications': app_count
            }
        }
    })

@auth_bp.route('/sync-mongo', methods=['POST'])
def sync_mongo():
    """Synchronizes all SQLite data to MongoDB."""
    result = sync_sqlite_to_mongo()
    return jsonify(result), (200 if result.get('success') else 400)

@auth_bp.route('/me', methods=['GET'])
@login_required
def get_current_user():
    user_id = g.current_user['sub']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, role, phone, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        if is_mongo_connected():
            user = mongo_get_user_by_id(user_id)
            if user:
                return jsonify({'success': True, 'user': user})
        return jsonify({'success': False, 'message': 'User profile not found.'}), 404
        
    return jsonify({
        'success': True,
        'user': dict(user)
    })

@auth_bp.route('/courses', methods=['GET'])
def get_courses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT code, name, department, seats, min_gpa, min_entrance FROM courses ORDER BY name ASC")
    courses = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({'success': True, 'courses': courses})
