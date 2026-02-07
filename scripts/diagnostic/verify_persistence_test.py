
import requests
import json
import time

BASE_URL = "http://localhost:8000"
PROJECT_ID = "TEST-VERIFY-001"

def test_persistence():
    print(f"Testing persistence for project {PROJECT_ID}...")
    
    # 1. Health Check
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"Server not running? Error: {e}")
        return

    # 2. Analyze Requirement (Triggers Save)
    payload = {
        "project_id": PROJECT_ID,
        "requirement": {
            "description": "A verified cat video persistence test",
            "duration": 15,
            "style": "documentary"
        }
    }
    
    print("\nSending analyze request...")
    try:
        resp = requests.post(f"{BASE_URL}/api/analyze-requirement", json=payload)
        if resp.status_code == 200:
            print("Analyze success!")
            print(json.dumps(resp.json(), indent=2, ensure_ascii=False)[:200] + "...")
        else:
            print(f"Analyze failed: {resp.status_code} - {resp.text}")
            return
    except Exception as e:
        print(f"Analyze request error: {e}")
        return

    # 3. Retrieve State (Verify Persistence)
    print("\nRetrieving project state...")
    try:
        resp = requests.get(f"{BASE_URL}/api/project/{PROJECT_ID}/state")
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                state = data.get("state", {})
                print(f"DEBUG_STATE_KEYS: {list(state.keys())}")
                if "requirement" in state:
                    print(f"DEBUG_REQ: {state['requirement']}")
                req_saved = state.get("requirement", {})
                print(f"State retrieved successfully!")
                print(f"Saved Description: {req_saved.get('description')}")
                
                if req_saved.get("description") == payload["requirement"]["description"]:
                    print("✅ VERIFICATION PASSED: Requirement persisted correcty.")
                else:
                    print("❌ VERIFICATION FAILED: Description mismatch.")
            else:
                print(f"State retrieval returned success=False: {data}")
        else:
            print(f"Get state failed: {resp.status_code} - {resp.text}")
    except Exception as e:
        print(f"Get state error: {e}")

if __name__ == "__main__":
    test_persistence()
