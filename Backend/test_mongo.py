"""
MongoDB Connection and Diagnostics Test Utility
Run this script to verify MongoDB connection:
    python test_mongo.py
"""

import os
import sys

# Add Backend to path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'Backend')
sys.path.insert(0, BACKEND_DIR)

from config import MONGO_URI, MONGO_DB_NAME
import mongo_db

def test_connection():
    print("=" * 70)
    print("  ADMISSION SYSTEM - MONGODB CONNECTION VERIFICATION")
    print("=" * 70)
    
    # Mask password for display
    safe_uri = MONGO_URI
    if "@" in safe_uri:
        prefix = safe_uri.split("@")[0]
        suffix = safe_uri.split("@")[1]
        protocol = prefix.split("://")[0]
        safe_uri = f"{protocol}://****:****@{suffix}"
        
    print(f"[Config] Target URI      : {safe_uri}")
    print(f"[Config] Target Database : {MONGO_DB_NAME}\n")

    # Step 1: Check pymongo module
    try:
        import pymongo
        print(f"[1/4] PyMongo library is installed (Version: {pymongo.__version__})")
    except ImportError:
        print("[1/4] [FAILED] PyMongo is NOT installed.")
        print("      To install, please run: pip install pymongo")
        print("      The system will continue running using SQLite fallback.")
        print("=" * 70)
        return

    # Step 2: Test live connection
    print("[2/4] Testing connection to MongoDB server...")
    client = mongo_db.get_mongo_client()
    if client is None:
        print(f"[2/4] [FAILED] Could not connect to MongoDB.")
        print(f"      Details: {mongo_db._connection_error}")
        print("\n      Troubleshooting Steps:")
        print("      - If using Local MongoDB: Start the service (e.g. net start MongoDB or mongod)")
        print("      - If using MongoDB Atlas: Check MONGO_URI in .env file (ensure username/password/whitelist IP)")
        print("=" * 70)
        return

    print("      [SUCCESS] Connected to MongoDB server successfully!")

    # Step 3: Check database & collections
    print(f"[3/4] Accessing database '{MONGO_DB_NAME}'...")
    db = client[MONGO_DB_NAME]
    collections = db.list_collection_names()
    print(f"      Existing collections: {collections if collections else '(None yet)'}")

    # Step 4: Sync SQLite data to MongoDB
    print("[4/4] Synchronizing initial data from SQLite to MongoDB...")
    sync_result = mongo_db.sync_sqlite_to_mongo()
    if sync_result.get('success'):
        print(f"      [SUCCESS] {sync_result.get('message')}")
    else:
        print(f"      [NOTICE] {sync_result.get('message')}")

    print("\n" + "=" * 70)
    print("  STATUS: MONGODB IS FULLY CONFIGURED & READY FOR USE!")
    print("=" * 70)

if __name__ == '__main__':
    test_connection()

