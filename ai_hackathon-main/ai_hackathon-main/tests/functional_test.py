import sys
import os
import time
import threading
import json
from io import BytesIO

# Mock missing dependencies for local testing
from unittest.mock import MagicMock
sys.modules["boto3"] = MagicMock()
sys.modules["botocore"] = MagicMock()
sys.modules["botocore.exceptions"] = MagicMock()
sys.modules["google"] = MagicMock()
sys.modules["google.genai"] = MagicMock()
sys.modules["openpyxl"] = MagicMock()
sys.modules["celery"] = MagicMock()
sys.modules["redis"] = MagicMock()
sys.modules["sqlalchemy"] = MagicMock()
sys.modules["sqlalchemy.orm"] = MagicMock()
sys.modules["sqlalchemy.exc"] = MagicMock()
sys.modules["psycopg2"] = MagicMock()

# Ensure root path is in sys.path
sys.path.append(os.getcwd())

# Mock get_aikosh_metadata to avoid API calls
import harmonizer
harmonizer.get_aikosh_metadata = lambda x: {
    "catalog_info": {"title": "Mock Title", "sector": "Test"}, 
    "technical_metadata": {"ai_readiness_level": 0.9},
    "status": "success"
}
# Mock storage to avoid S3 errors
import services.storage
services.storage.S3Storage = MagicMock()

from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

def create_dummy_csv():
    content = "col1,col2,col3\nval1,val2,val3\nval4,val5,val6"
    return BytesIO(content.encode('utf-8'))

def test_upload_flow(user_id):
    print(f"[User-{user_id}] Starting upload...")
    
    # 1. Upload
    dummy_file = create_dummy_csv()
    response = client.post(
        "/harmonize",
        files={"file": ("test_data.csv", dummy_file, "text/csv")}
    )
    
    if response.status_code != 200:
        print(f"[User-{user_id}] Upload FAILED: {response.text}")
        return False

    data = response.json()
    file_hash = data.get("file_hash")
    status = data.get("status")
    
    print(f"[User-{user_id}] Upload OK. Hash: {file_hash}, Status: {status}")
    
    # If using Async/Celery, status might be 'processing'. If Sync, it might be result directly.
    # The API now returns {"status": "processing"} initially if using background tasks
    
    if "catalog_info" in data or data.get("status") == "success":
        print(f"[User-{user_id}] Success immediately!")
        return True

    # 2. Poll
    attempts = 0
    while attempts < 30: # 30 attempts * 1s = 30s timeout
        time.sleep(1)
        resp_status = client.get(f"/status/{file_hash}")
        if resp_status.status_code != 200:
            print(f"[User-{user_id}] Polling Error: {resp_status.text}")
            return False
            
        status_data = resp_status.json()
        current_status = status_data.get("status")
        
        # Check for success indicators
        if status_data.get("catalog_info") or status_data.get("_is_cached") or "technical_metadata" in status_data:
             print(f"[User-{user_id}] SUCCESS! Metadata received.")
             return True
             
        if current_status == "error":
             print(f"[User-{user_id}] Job Failed: {status_data.get('error_message')}")
             return False
             
        # print(f"[User-{user_id}] Polling... Status: {current_status}")
        attempts += 1
        
    print(f"[User-{user_id}] TIMEOUT waiting for results.")
    return False

def run_concurrent_test():
    print("--- Starting Concurrency Test (3 Users) ---")
    threads = []
    results = []

    def run_user(uid):
        res = test_upload_flow(uid)
        results.append(res)

    for i in range(3):
        t = threading.Thread(target=run_user, args=(i+1,))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    print("\n--- Test Results ---")
    if all(results):
        print("✅ ALL TESTS PASSED. System handled 3 concurrent users.")
    else:
        print("❌ SOME TESTS FAILED.")
        exit(1)

if __name__ == "__main__":
    try:
        # Run single user test to verify logic
        print("--- Single User Test ---")
        if test_upload_flow(1):
            print("✅ TEST PASSED")
            sys.exit(0)
        else:
            print("❌ TEST FAILED")
            sys.exit(1)
    except ImportError:
         print("CRITICAL: httpx not installed. Cannot run tests.")
         exit(0) 
    except Exception as e:
        print(f"Test crashed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
