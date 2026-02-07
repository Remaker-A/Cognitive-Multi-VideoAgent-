import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def list_models():
    api_key = os.getenv("VIDEO_API_KEY")
    api_url = os.getenv("VIDEO_API_URL", "https://api.omnimaas.com/v1")
    
    url = f"{api_url}/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30, proxies={"http": None, "https": None})
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            models = response.json()
            print("Available models:")
            for m in models.get("data", []):
                print(f" - {m.get('id')}")
        else:
            print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_models()
