
import asyncio
import sys
import os
import logging
from dotenv import load_dotenv

# Setup paths
sys.path.append(os.path.join(os.getcwd(), 'src'))
sys.path.append(os.path.join(os.getcwd(), 'src/interfaces/api'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("debug_server_api")

# Verify Qwen Adapter Import
try:
    from src.adapters.implementations import QwenAdapter
    logger.info("QwenAdapter importable.")
except ImportError as e:
    logger.error(f"Failed to import QwenAdapter: {e}")

# Import app components
# We can't easily import 'app' without triggering uvicorn things if we aren't careful, 
# but importing the module usually is fine if main block guards it.
from src.interfaces.api.api_server import generate_image, ImageInput

async def test_server_generation():
    logger.info("Starting test_server_generation")
    
    # Mock Input
    input_data = ImageInput(
        project_id="test_proj_debug",
        shot=1,
        shot_info={"scene": "A futuristic city with flying cars", "action": "traffic moving smoothly"}
    )
    
    logger.info("Calling generate_image endpoint function directly...")
    try:
        result = await generate_image(input_data)
        logger.info(f"Result: {result}")
        if result.get("success"):
            logger.info("SUCCESS: Image generated.")
        else:
            logger.info(f"FAILURE: {result.get('error')}")
            if "placeholder" in result.get("image_url", ""):
                 logger.info("Used Placeholder Fallback.")
                 
    except Exception as e:
        logger.error(f"Function raised exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_server_generation())
