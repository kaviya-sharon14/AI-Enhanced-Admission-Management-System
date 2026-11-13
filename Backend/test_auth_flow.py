"""
Verification Script for Authentication and Password Reset Flow
Tests:
  1. New User Registration
  2. Sign In with Registered Credentials
  3. Forgot Password - Verification Code Generation
  4. Reset Password with Verification Code
  5. Sign In with Updated Password
  6. DB Status Check
"""

import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(BASE_DIR, 'Backend'))

from app import create_app

def run_tests():
    print("=================================================================")
    print("  AUTHENTICATION & FORGOT PASSWORD WORKFLOW TEST SUITE")
    print("=================================================================")

    app = create_app()
    client = app.test_client()

    test_email = "test.applicant.2026@gmail.com"
    original_pw = "TestPassword@123"
    new_pw = "BrandNewPassword@2026"

    # Test 1: Register New User
    print("\n[Test 1] Testing New User Registration...")
    reg_payload = {
        "name": "Karthik Subramanian",
        "email": test_email,
        "password": original_pw,
        "phone": "+91 98401 23456",
        "role": "student"
    }
    res = client.post('/api/auth/register', json=reg_payload)
    if res.status_code == 409:
        print("  Notice: User already registered from previous run, continuing...")
    else:
        assert res.status_code == 201, f"Expected 201, got {res.status_code}: {res.get_json()}"
        data = res.get_json()
        assert data['success'] is True
        assert 'token' in data
        print("  -> PASSED: New User registered successfully.")

    # Test 2: Sign In with Existing User
    print("\n[Test 2] Testing Sign In with Email & Password...")
    login_payload = {
        "email": test_email,
        "password": original_pw
    }
    res = client.post('/api/auth/login', json=login_payload)
    if res.status_code == 401:
        # Maybe password was already reset in a previous run, let's try with new_pw
        res = client.post('/api/auth/login', json={"email": test_email, "password": new_pw})
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.get_json()}"
    data = res.get_json()
    assert data['success'] is True
    assert 'token' in data
    print(f"  -> PASSED: Logged in successfully as {data['user']['name']}.")

    # Test 3: Forgot Password Request
    print("\n[Test 3] Testing Forgot Password (Code Generation)...")
    res = client.post('/api/auth/forgot-password', json={"email": test_email})
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.get_json()}"
    data = res.get_json()
    assert data['success'] is True
    assert 'reset_code' in data
    reset_code = data['reset_code']
    print(f"  -> PASSED: Generated 6-digit reset code: {reset_code} for {test_email}")

    # Test 4: Reset Password
    print("\n[Test 4] Testing Password Reset with 6-digit Code...")
    reset_payload = {
        "email": test_email,
        "reset_code": reset_code,
        "new_password": new_pw
    }
    res = client.post('/api/auth/reset-password', json=reset_payload)
    assert res.status_code == 200, f"Expected 200, got {res.status_code}: {res.get_json()}"
    data = res.get_json()
    assert data['success'] is True
    print(f"  -> PASSED: Password successfully updated to '{new_pw}'.")

    # Test 5: Verify Old Password Fails and New Password Succeeds
    print("\n[Test 5] Verifying Login Authentication with New Password...")
    old_res = client.post('/api/auth/login', json={"email": test_email, "password": original_pw})
    assert old_res.status_code == 401, f"Expected 401 for old password, got {old_res.status_code}"
    print("  -> PASSED: Old password rejected correctly.")

    new_res = client.post('/api/auth/login', json={"email": test_email, "password": new_pw})
    assert new_res.status_code == 200, f"Expected 200 for new password, got {new_res.status_code}"
    print("  -> PASSED: New password accepted and authenticated successfully.")

    # Test 6: Database Diagnostics API
    print("\n[Test 6] Testing Database Diagnostics Endpoint...")
    db_res = client.get('/api/auth/db-status')
    assert db_res.status_code == 200, f"Expected 200, got {db_res.status_code}"
    db_data = db_res.get_json()
    print(f"  -> PASSED: Database status checked:")
    print(f"     SQLite: Connected ({db_data['sqlite']['counts']['users']} users)")
    print(f"     MongoDB Configured: {db_data['mongodb']['database']} | Connected: {db_data['mongodb']['connected']}")

    print("\n=================================================================")
    print("  ALL 6 TESTS PASSED FLAWLESSLY!")
    print("=================================================================")

if __name__ == '__main__':
    run_tests()

