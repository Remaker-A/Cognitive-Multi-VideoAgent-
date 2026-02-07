import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Load env
load_dotenv()

# Add project root
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.adapters.implementations.sora2_adapter import Sora2Adapter

async def test_simple_generate():
    api_key = os.getenv("VIDEO_API_KEY")
    if not api_key:
        print("No API key found")
        return

    adapter = Sora2Adapter(api_key=api_key)
    print(f"Testing with API URL: {adapter.api_url}")
    
    try:
        result = await adapter.generate(
            prompt="A cute cat blinking",
            duration=4
        )
        print(f"Result Success: {result.success}")
        if result.success:
            print(f"Video URL: {result.artifact_url}")
            print(f"Metadata: {result.metadata}")
        else:
            print(f"Error: {result.error}")
            
    except Exception as e:
        print(f"Exception: {e}")
    finally:
        await adapter.close()

if __name__ == "__main__":
    try:
        asyncio.run(test_simple_generate())
    except Exception as e:
        print(f"Runner Exception: {e}")
