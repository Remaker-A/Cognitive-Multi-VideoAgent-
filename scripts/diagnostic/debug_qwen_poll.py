
import os
import time
import requests
import json
import traceback
from dotenv import load_dotenv

# Setup log file
LOG_FILE = "qwen_polling_test.log"
def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

# Clear log
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("Starting polling test (NO PROXY)\n")

try:
    # Load env
    load_dotenv()

    API_KEY = os.getenv("IMAGE_API_KEY") or os.getenv("MODELSCOPE_API_KEY")
    # Force ModelScope URL if not set
    BASE_URL = os.getenv("IMAGE_API_URL", "https://api-inference.modelscope.cn/")
    # MODEL = os.getenv("IMAGE_MODEL", "Qwen/Qwen-Image-2512")
    MODEL = "damo/cv_wanx-text-to-image_tiny"

    if not BASE_URL.endswith("/"):
        BASE_URL += "/"

    url = f"{BASE_URL}v1/images/generations"

    # Disable proxy
    os.environ['HTTP_PROXY'] = ''
    os.environ['HTTPS_PROXY'] = ''
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
         "X-ModelScope-Async-Mode": "true"
    }
    
    data = {"model": MODEL, "prompt": "A cute cat"}
    
    log(f"Submitting task to {url}...")
    session = requests.Session()
    session.trust_env = False
    
    resp = session.post(url, headers=headers, json=data, timeout=30)
    log(f"Status Code: {resp.status_code}")
    
    if resp.status_code == 200:
        json_resp = resp.json()
        if "task_id" in json_resp:
             task_id = json_resp['task_id']
             log(f"Got task_id: {task_id}")
             
             # Test Endpoint 1: v1/tasks/
             poll_url_1 = f"{BASE_URL}v1/tasks/{task_id}"
             
             # Test Endpoint 2: api-inference/v1/tasks/ (Common ModelScope path)
             poll_url_2 = f"{BASE_URL}api-inference/v1/tasks/{task_id}"
             
             log(f"Testing Poll URL 1: {poll_url_1}")
             time.sleep(2)
             resp1 = session.get(poll_url_1, headers={"Authorization": f"Bearer {API_KEY}"})
             log(f"Resp 1 Code: {resp1.status_code}")
             log(f"Resp 1 Body: {resp1.text}")
             
             log(f"Testing Poll URL 2: {poll_url_2}")
             time.sleep(1)
             resp2 = session.get(poll_url_2, headers={"Authorization": f"Bearer {API_KEY}"})
             log(f"Resp 2 Code: {resp2.status_code}")
             log(f"Resp 2 Body: {resp2.text}")
             
        else:
             log("No task_id in response")
             log(resp.text)
    else:
        log(f"Request failed: {resp.text}")

except Exception as e:
    log(f"Exception: {e}")
