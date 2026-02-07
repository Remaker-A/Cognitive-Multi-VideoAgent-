import asyncio
import os
import httpx
from dotenv import load_dotenv
import json

load_dotenv()

async def test_retrieve():
    file_id = "359137816523033" # From previous run
    api_key = os.getenv("API_KEY")
    url = f"https://api.minimaxi.com/v1/files/retrieve?file_id={file_id}"
    
    async with httpx.AsyncClient(timeout=10, trust_env=True) as client:
        response = await client.get(
            url,
            headers={"Authorization": f"Bearer {api_key}"}
        )
        print(f"Status: {response.status_code}")
        print(f"Body: {response.text}")

if __name__ == "__main__":
    asyncio.run(test_retrieve())
