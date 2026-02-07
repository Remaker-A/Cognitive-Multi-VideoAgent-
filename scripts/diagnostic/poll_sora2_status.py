import os
import requests
import json
import time
from dotenv import load_dotenv

load_dotenv()

def poll_status(video_id):
    api_key = os.getenv("VIDEO_API_KEY")
    url = f"https://api.omnimaas.com/v1/videos/{video_id}"
    
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    
    print(f"Polling status for Video ID: {video_id}")
    
    for i in range(5):
        try:
            response = requests.get(url, headers=headers, timeout=30, proxies={"http": None, "https": None})
            if response.status_code == 200:
                data = response.json()
                print(f"Status: {data.get('status')} | Progress: {data.get('progress')}%")
                if data.get('status') == 'completed':
                    print(f"✅ Video Ready! URL: {data.get('video_url')}")
                    return
                elif data.get('status') == 'failed':
                    print(f"❌ Video Failed: {data.get('error')}")
                    return
            else:
                print(f"Error checking status: {response.status_code}")
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(10)

if __name__ == "__main__":
    # Use the ID from the previous run
    poll_status("video_6978595108688193b17923ff6b17386808fb1739e87de868")
