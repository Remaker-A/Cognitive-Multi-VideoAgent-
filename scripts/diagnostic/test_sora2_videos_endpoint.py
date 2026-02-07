import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_user_payload():
    api_key = os.getenv("VIDEO_API_KEY")
    url = "https://api.omnimaas.com/v1/videos" # Based on historical info
    
    data = {
        "model": "sora-2",
        "prompt": "可爱鸭子在游泳"
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    print(f"Testing Endpoint: {url}")
    print(f"Payload: {json.dumps(data, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30, proxies={"http": None, "https": None})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_user_payload()
