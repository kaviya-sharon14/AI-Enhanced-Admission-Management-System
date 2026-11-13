"""
Authentication and Authorization Utilities using PyJWT
"""

import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g
from config import SECRET_KEY

def generate_jwt(user_id: int, email: str, role: str, name: str) -> str:
    payload = {
        'sub': str(user_id),
        'user_id': user_id,
        'email': email,
        'role': role,
        'name': name,
        'iat': datetime.datetime.now(datetime.timezone.utc),
        'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=7)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_jwt(token: str) -> dict:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        if 'sub' in data:
            data['sub'] = int(data['sub'])
        return data
    except Exception as e:
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Authentication required. Missing or invalid Bearer token.'}), 401
            
        token = auth_header.split(' ')[1]
        decoded = verify_jwt(token)
        if not decoded:
            return jsonify({'success': False, 'message': 'Token is invalid or expired. Please log in again.'}), 401
            
        g.current_user = decoded
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': 'Administrative privileges required.'}), 401
            
        token = auth_header.split(' ')[1]
        decoded = verify_jwt(token)
        if not decoded or decoded.get('role') != 'admin':
            return jsonify({'success': False, 'message': 'Access forbidden. Admin role required.'}), 403
            
        g.current_user = decoded
        return f(*args, **kwargs)
    return decorated_function
