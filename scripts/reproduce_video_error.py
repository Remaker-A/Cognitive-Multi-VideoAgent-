
import asyncio
import os
import sys
import platform
import logging


# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src/interfaces/api'))

# Fix for Windows Event Loop
if platform.system() == 'Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from dotenv import load_dotenv
load_dotenv()

from video_generator import VideoGenerator

async def test_video_gen():
    # Configure logging to stdout
    root = logging.getLogger()
    if not root.handlers:
        root.setLevel(logging.DEBUG)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        root.addHandler(handler)

    print("Testing VideoGenerator...")
    vg = VideoGenerator()
    print(f"API URL: {vg.base_url}")
    print(f"Model: {vg.model}")
    print(f"Is Native: {'minimaxi.com' in vg.base_url}")
    
    try:
        # Use a very short timeout for testing or just invoke it
        # Note: The generate method now polls. It might take time.
        # We will wait a bit to see if it submits successfully.
        
        print("Starting generation...")
        result = await vg.generate(
            prompt="A cinematic shot of a cat sitting on a roof at sunset, 4k, implementation of testing.",
            duration=6,
            resolution="1080P"
        )
        print("Result:", result)
        
    except Exception as e:
        print(f"Error caught: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await vg.close()

if __name__ == "__main__":
    asyncio.run(test_video_gen())
