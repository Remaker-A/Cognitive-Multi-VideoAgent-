import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_custom_payload():
    api_key = os.getenv("VIDEO_API_KEY")
    api_url = os.getenv("VIDEO_API_URL", "https://api.omnimaas.com/v1")
    
    # 尝试多个可能的端点
    endpoints = [
        f"{api_url}/chat/completions",
        f"{api_url}/videos/generations",
        f"{api_url}/images/generations"
    ]
    
    data = {
        "model": "sora-2",
        "prompt": "可爱鸭子在游泳"
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    for url in endpoints:
        print(f"\n--- Testing Endpoint: {url} ---")
        try:
            response = requests.post(url, headers=headers, json=data, timeout=30, proxies={"http": None, "https": None})
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_custom_payload()
