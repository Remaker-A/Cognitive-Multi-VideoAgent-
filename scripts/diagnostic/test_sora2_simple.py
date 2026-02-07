import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test():
    api_key = os.getenv("VIDEO_API_KEY")
    api_url = os.getenv("VIDEO_API_URL", "https://api.omnimaas.com/v1")
    model = os.getenv("VIDEO_MODEL", "sora-2")
    
    url = f"{api_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "Generate a short video of a robot dancing."}]
    }
    
    print(f"Request URL: {url}")
    print(f"Request Model: {model}")
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30, proxies={"http": None, "https": None})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test()
