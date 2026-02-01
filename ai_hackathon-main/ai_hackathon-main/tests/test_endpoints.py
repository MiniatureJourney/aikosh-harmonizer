from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path to import api
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)
os.chdir(project_root)

from api import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    # Check if index.html content is returned (look for title)
    assert "AIKosh" in response.text
    print("SUCCESS: GET / returned index.html")

def test_cors_headers():
    response = client.options("/", headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"})
    # Starlette/FastAPI TestClient handles middleware? 
    # Usually OPTIONS might not be automatically handled unless explicitly defined or by CORSMiddleware
    # But simple GET with Origin should show Access-Control-Allow-Origin
    
    response = client.get("/", headers={"Origin": "http://example.com"})
    assert response.headers["access-control-allow-origin"] == "*"
    print("SUCCESS: CORS headers present")

if __name__ == "__main__":
    try:
        test_read_main()
        test_cors_headers()
        print("\nALL SYSTEM CHECKS PASSED.")
    except Exception as e:
        print(f"\nFAILED: {e}")
        sys.exit(1)
