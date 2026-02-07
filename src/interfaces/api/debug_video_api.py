import asyncio
import os
import sys
import httpx
from pathlib import Path
from dotenv import load_dotenv
import json

# 加载环境变量
load_dotenv()

# 添加 src 到路径
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

from interfaces.api.video_generator import VideoGenerator

async def debug_response():
    api_key = os.getenv("API_KEY")
    api_url = os.getenv("VIDEO_API_URL", "https://api.minimaxi.com/v1/video_generation")
    model = os.getenv("VIDEO_MODEL", "MiniMax-Hailuo-2.3")
    
    print(f"Testing with Model: {model}")
    print(f"API URL: {api_url}")
    
    prompt = "A small mouse dancing"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": model,
                    "prompt": prompt,
                    "duration": 6,
                    "resolution": "1080P"
                }
            )
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    asyncio.run(debug_response())
