import sys
import os
import importlib
import traceback

print("--- AIKosh Deployment Verification ---")

def check_import(module_name):
    try:
        importlib.import_module(module_name)
        print(f"[OK] Module found: {module_name}")
        return True
    except ImportError as e:
        print(f"[FAIL] Missing module: {module_name} ({e})")
        return False

# 1. Dependency Check
print("\n1. Checking Dependencies...")
dependencies = [
    "fastapi", "uvicorn", "boto3", "sqlalchemy", 
    "psycopg2", "celery", "redis", "google.genai", 
    "openpyxl", "dotenv"
]
# Note: psycopg2 might fail in some non-binary environments, but we installed psycopg2-binary
missing = []
for dep in dependencies:
    # Handle hyphens/names
    mod = dep.replace("-", "_")
    if dep == "google.genai": mod = "google.genai"
    if dep == "openpyxl": mod = "openpyxl"
    
    if not check_import(mod):
        missing.append(dep)

if missing:
    print(f"CRITICAL: The following dependencies are missing: {missing}")
    # Don't exit yet, try to check code validity

# 2. Check Services
print("\n2. Verifying Service Initialization...")
try:
    # We must ensure we are in the right directory or pythonpath handles it
    sys.path.append(os.getcwd())
    
    from services.storage import get_storage_service
    from services.database import get_db_service
    
    storage = get_storage_service()
    print(f"[OK] Storage Service initialized: {type(storage).__name__}")
    
    db = get_db_service()
    print(f"[OK] Database Service initialized: {type(db).__name__}")
    
except Exception as e:
    print(f"[FAIL] Service Initialization Failed: {e}")
    traceback.print_exc()

# 3. Check API Startup (Static Analysis / Import)
print("\n3. Verifying API Import...")
try:
    from api import app
    print("[OK] FastAPI 'app' object imported successfully.")
except Exception as e:
    print(f"[FAIL] Failed to import 'api.py'. Application will not start: {e}")
    traceback.print_exc()

print("\n--- Verification Complete ---")
