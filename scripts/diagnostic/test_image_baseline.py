import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def test_image():
    api_key = os.getenv("IMAGE_API_KEY")
    api_url = os.getenv("IMAGE_API_URL", "https://api.omnimaas.com/v1")
    model = os.getenv("IMAGE_MODEL", "gemini-3-pro-image-preview")
    
    url = f"{api_url}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "Generate a picture of a cat."}]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30, proxies={"http": None, "https": None})
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_image()
