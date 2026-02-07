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

async def debug_to_file():
    api_key = os.getenv("API_KEY")
    generator = VideoGenerator(api_key)
    
    log_file = "video_api_debug_log.json"
    logs = []
    
    def log(msg, data=None):
        entry = {"msg": msg}
        if data: entry["data"] = data
        logs.append(entry)
        print(msg)

    prompt = "A small mouse dancing"
    
    log("Starting generation...")
    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            # 1. Start Task
            response = await client.post(
                generator.api_url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": generator.model,
                    "prompt": prompt,
                    "duration": 6,
                    "resolution": "1080P"
                }
            )
            
            init_data = response.json()
            log("Initial Response", init_data)
            
            task_id = init_data.get("task_id")
            if not task_id:
                log("No task_id found!")
                return

            # 2. Poll
            query_url = generator.api_url.replace("video_generation", "query/video_generation")
            poll_url = f"{query_url}?task_id={task_id}"
            log(f"Polling URL: {poll_url}")
            
            for i in range(20): # Max 20 polls
                await asyncio.sleep(10)
                poll_resp = await client.get(
                    poll_url,
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                poll_data = poll_resp.json()
                log(f"Poll {i+1}", poll_data)
                
                status = poll_data.get("status")
                if status in ["Success", "Fail"]:
                    break
                    
    except Exception as e:
        log(f"Error: {repr(e)}")
    finally:
        with open(log_file, "w", encoding="utf8") as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)
        log(f"Logs written to {log_file}")

if __name__ == "__main__":
    asyncio.run(debug_to_file())
