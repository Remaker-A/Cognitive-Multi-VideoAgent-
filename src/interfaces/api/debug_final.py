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

async def main():
    api_key = os.getenv("API_KEY")
    generator = VideoGenerator(api_key)
    
    prompt = "A cute cat running in the garden, 4k, cinematic"
    print(f"Testing generation with prompt: {prompt}")
    
    result = await generator.generate(prompt=prompt)
    
    print("\n" + "="*50)
    print("FINAL RESULT:")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print("="*50)

if __name__ == "__main__":
    asyncio.run(main())
