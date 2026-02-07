import httpx
import json

def test_api():
    base_url = "http://localhost:8000"
    
    print("1. Testing Health Check...")
    try:
        r = httpx.get(f"{base_url}/health")
        print(f"Status: {r.status_code}, Body: {r.text}")
    except Exception as e:
        print(f"Health Check Failed: {e}")
        return

    print("\n2. Testing Requirement Analysis...")
    payload = {
        "project_id": "test-project-1",
        "requirement": {
            "description": "A small robot exploring Mars",
            "duration": 5,
            "quality_tier": "standard",
            "style": "cinematic"
        }
    }
    try:
        r = httpx.post(f"{base_url}/api/analyze-requirement", json=payload, timeout=60.0)
        print(f"Status: {r.status_code}")
        if r.status_code == 200:
            print("Successfully analyzed requirement.")
        else:
            print(f"Error: {r.text}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    test_api()
