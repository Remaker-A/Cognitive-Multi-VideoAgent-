
import asyncio
import os
import sys

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.adapters.implementations.qwen_adapter import QwenAdapter
import logging

logging.basicConfig(level=logging.INFO)

async def test_qwen():
    api_key = "ms-1a3476bb-1a6a-4f67-9a5a-94e5e18bb60b"
    base_url = "https://api-inference.modelscope.cn/"
    
    print(f"Testing QwenAdapter with:")
    print(f"API Key: {api_key[:10]}...")
    print(f"Base URL: {base_url}")
    
    adapter = QwenAdapter(api_key=api_key, base_url=base_url)
    
    try:
        print("Sending generation request...")
        result = await adapter.generate(
            prompt="A cute cat sitting on a bench",
            width=1328,
            height=1328
        )
        
        print(f"Result success: {result.success}")
        if result.success:
            print(f"Image URL: {result.artifact_url}")
        else:
            print(f"Error: {result.error}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_qwen())
