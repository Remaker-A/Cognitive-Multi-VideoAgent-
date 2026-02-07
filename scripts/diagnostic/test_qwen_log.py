
import asyncio
import os
import sys
import logging

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'src'))

from src.adapters.implementations.qwen_adapter import QwenAdapter

# Configure logging to file
logging.basicConfig(
    filename='qwen_test_log.txt',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

async def test_qwen():
    api_key = "ms-1a3476bb-1a6a-4f67-9a5a-94e5e18bb60b"
    base_url = "https://api-inference.modelscope.cn/"
    
    logging.info(f"Testing QwenAdapter with 1328x1328")
    
    adapter = QwenAdapter(api_key=api_key, base_url=base_url)
    
    try:
        logging.info("Sending generation request...")
        result = await adapter.generate(
            prompt="A cute cat sitting on a bench",
            width=1328,
            height=1328
        )
        
        logging.info(f"Result success: {result.success}")
        if result.success:
            logging.info(f"Image URL: {result.artifact_url}")
        else:
            logging.info(f"Error: {result.error}")
            
    except Exception as e:
        logging.error(f"Exception: {e}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(test_qwen())
