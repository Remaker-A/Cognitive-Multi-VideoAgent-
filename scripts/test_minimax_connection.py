
import httpx
import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def test_connect():
    url = "https://api.minimaxi.com/v1/video_generation"
    
    sk_key = os.getenv("IMAGE_API_KEY", "") # starts with sk-
    uuid_key = os.getenv("VIDEO_API_KEY", "") # starts with 30ac...
    
    print(f"SK Key: {sk_key[:5]}...")
    print(f"UUID Key: {uuid_key[:5]}...")
    
    payload = {
        "model": "MiniMax-Hailuo-2.3",
        "prompt": "test video generation",
    }
    
    # Test 1: SK Key only
    print("\nTest 1: SK Key only")
    headers = {
        "Authorization": f"Bearer {sk_key}",
        "Content-Type": "application/json"
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers)
            print(f"Status: {resp.status_code}")
            print(f"Body: {resp.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: SK Key + UUID as Group ID
    print("\nTest 2: SK Key + UUID as Group ID")
    headers = {
        "Authorization": f"Bearer {sk_key}",
        "Content-Type": "application/json",
        "Minimax-Group-Id": uuid_key
    }
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers)
            print(f"Status: {resp.status_code}")
            try:
                data = resp.json()
                if "task_id" in data:
                    print(f"SUCCESS: Got task_id {data['task_id']}")
                else:
                    print(f"FAILURE: Body: {resp.text[:200]}")
            except:
                 print(f"FAILURE: Body: {resp.text[:200]}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import platform
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(test_connect())
