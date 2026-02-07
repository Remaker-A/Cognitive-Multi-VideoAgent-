
import os
import time
import requests
import json
import traceback
from dotenv import load_dotenv

# Setup log file
LOG_FILE = "qwen_debug_noproxy.log"
def log(msg):
    print(msg)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(str(msg) + "\n")

# Clear log
with open(LOG_FILE, "w", encoding="utf-8") as f:
    f.write("Starting debug session (NO PROXY)\n")

try:
    # Load env
    load_dotenv()

    API_KEY = os.getenv("IMAGE_API_KEY") or os.getenv("MODELSCOPE_API_KEY")
    BASE_URL = os.getenv("IMAGE_API_URL", "https://api-inference.modelscope.cn/")
    MODEL = os.getenv("IMAGE_MODEL", "Qwen/Qwen-Image-2512")

    if not BASE_URL.endswith("/"):
        BASE_URL += "/"

    url = f"{BASE_URL}v1/images/generations"

    log(f"Testing URL: {url}")
    
    # Disable proxy by setting empty env vars for this process
    os.environ['HTTP_PROXY'] = ''
    os.environ['HTTPS_PROXY'] = ''
    os.environ['http_proxy'] = ''
    os.environ['https_proxy'] = ''
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
         "X-ModelScope-Async-Mode": "true"
    }
    
    data = {
        "model": MODEL,
        "prompt": "A cute cat",
    }
    
    log("Sending request (Proprietary NO PROXY)...")
    
    # Use session with trust_env=False just in case
    session = requests.Session()
    session.trust_env = False
    
    resp = session.post(url, headers=headers, json=data, timeout=30)
    log(f"Status Code: {resp.status_code}")
    
    if resp.status_code == 200:
        json_resp = resp.json()
        log(f"Response keys: {list(json_resp.keys())}")
        
        if "task_id" in json_resp:
             task_id = json_resp['task_id']
             log(f"SUCCESS: Got task_id {task_id}")
             
             poll_url = f"{BASE_URL}v1/tasks/{task_id}"
             log(f"Polling {poll_url}...")
             
             for i in range(10):
                 time.sleep(2)
                 try:
                     poll_resp = session.get(poll_url, headers={"Authorization": f"Bearer {API_KEY}"}, timeout=30)
                     poll_data = poll_resp.json()
                     status = poll_data.get('task_status')
                     log(f"Poll {i}: {status}")
                     
                     if status == 'FAILED':
                         log("Task FAILED DETAILS:")
                         log(json.dumps(poll_data, indent=2, ensure_ascii=False))
                         break
                         
                     if status == 'SUCCEED':
                         log("Task SUCCEEDED!")
                         log(json.dumps(poll_data, indent=2, ensure_ascii=False))
                         break
                 except Exception as e:
                     log(f"Poll error: {e}")
        else:
             log("Response does not contain task_id")
             log(resp.text)
    else:
        log(f"Request failed: {resp.text}")

except Exception as e:
    log(f"Exception: {e}")
    log(traceback.format_exc())
