import os
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

def test_sora2_api():
    api_key = os.getenv("VIDEO_API_KEY")
    api_url = os.getenv("VIDEO_API_URL", "https://api.omnimaas.com/v1")
    model = os.getenv("VIDEO_MODEL", "sora-2")
    
    endpoint = f"{api_url}/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": "Generate a 2-second video of a cute cat blinking."
            }
        ]
    }
    
    print(f"=== Request Information ===")
    print(f"URL: {endpoint}")
    print(f"Headers: {json.dumps({k: (v if k != 'Authorization' else 'Bearer ' + v[:10] + '...') for k, v in headers.items()}, indent=2)}")
    print(f"Payload: {json.dumps(payload, indent=2)}")
    print("\n" + "="*30 + "\n")
    
    try:
        with httpx.Client(timeout=60.0) as client:
            response = client.post(endpoint, headers=headers, json=payload)
            
            print(f"=== Response Information ===")
            print(f"Status Code: {response.status_code}")
            try:
                response_json = response.json()
                print(f"Response Body: {json.dumps(response_json, indent=2)}")
            except:
                print(f"Response Body (Raw): {response.text}")
                
            if response.status_code == 200:
                print("\n✅ Sora2 API is available!")
            else:
                print("\n❌ Sora2 API returned error.")
                
    except Exception as e:
        print(f"\n❌ Error connecting to Sora2 API: {e}")

if __name__ == "__main__":
    test_sora2_api()
