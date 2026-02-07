
import os
import time
import requests
import json
from dotenv import load_dotenv

# Load env
load_dotenv()

API_KEY = os.getenv("IMAGE_API_KEY") or os.getenv("MODELSCOPE_API_KEY")
BASE_URL = os.getenv("IMAGE_API_URL", "https://api-inference.modelscope.cn/")
MODEL = os.getenv("IMAGE_MODEL", "Qwen/Qwen-Image-2512")

if not BASE_URL.endswith("/"):
    BASE_URL += "/"

url = f"{BASE_URL}v1/images/generations"

print(f"Testing URL: {url}")
print(f"Model: {MODEL}")

def test_generate():
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
         "X-ModelScope-Async-Mode": "true"
    }
    
    data = {
        "model": MODEL,
        "prompt": "A cute cat",
    }
    
    print("Sending request...")
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"Status Code: {resp.status_code}")
        
        if resp.status_code == 200:
            json_resp = resp.json()
            if "task_id" in json_resp:
                 print(f"SUCCESS: Got task_id {json_resp['task_id']}")
                 # Try polling
                 task_id = json_resp['task_id']
                 poll_url = f"{BASE_URL}v1/tasks/{task_id}"
                 print(f"Polling {poll_url}...")
                 
                 for i in range(10):
                     time.sleep(2)
                     poll_resp = requests.get(poll_url, headers={"Authorization": f"Bearer {API_KEY}"}, timeout=30)
                     poll_data = poll_resp.json()
                     status = poll_data.get('task_status')
                     print(f"Poll {i}: {status}")
                     
                     if status == 'FAILED':
                         print("Task FAILED DETAILS:")
                         print(json.dumps(poll_data, indent=2, ensure_ascii=False))
                         break
                         
                     if status == 'SUCCEED':
                         print("Task SUCCEEDED!")
                         print(json.dumps(poll_data, indent=2, ensure_ascii=False))
                         break
            else:
                 print("Response does not contain task_id")
                 print(resp.text)
        else:
            print(f"Request failed: {resp.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_generate()
