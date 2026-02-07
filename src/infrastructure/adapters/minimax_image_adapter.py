import os
import aiohttp
import logging
from typing import Optional
from src.infrastructure.adapters.image_adapter import ImageModelAdapter
from src.infrastructure.adapters.schemas import ImageGenerationResult

from src.infrastructure.config_manager import ConfigManager

logger = logging.getLogger(__name__)

class MiniMaxImageAdapter(ImageModelAdapter):
    def __init__(self):
        super().__init__()
        # self.api_key and self.group_id handled dynamically in generate()
        self.base_url = "https://api.minimaxi.com/v1/image_generation"
    
    async def generate(
        self,
        prompt: str,
        width: int = 1280,
        height: int = 720,
        **kwargs
    ) -> ImageGenerationResult:
        # Load config dynamically
        api_key = ConfigManager.get("MINIMAX_IMAGE_API_KEY") or ConfigManager.get("IMAGE_API_KEY")
        group_id = ConfigManager.get("MINIMAX_GROUP_ID", "default")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "model": "image-01",
            "size": f"{width}x{height}" if "size" not in kwargs else kwargs["size"],
            "n": 1
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        return ImageGenerationResult(
                            success=False,
                            error=f"MiniMax API Error: {resp.status} - {error_text}"
                        )
                    
                    data = await resp.json()
                    # Parse MiniMax response logic (assuming standard OpenAI-like or custom)
                    # Note: Need to verify exact MiniMax response format. 
                    # Assuming data["images"][0]["url"] or similar based on typical APIs
                    # Re-checking api_server.py might be needed if format is unique.
                    
                    # Placeholder for specific parsing:
                    image_url = ""
                    if "images" in data and len(data["images"]) > 0:
                         image_url = data["images"][0].get("url", "")
                    elif "data" in data and len(data["data"]) > 0:
                         image_url = data["data"][0].get("url", "")
                    
                    if image_url:
                        return ImageGenerationResult(
                            success=True,
                            image_url=image_url
                        )
                    else:
                        return ImageGenerationResult(success=False, error=f"No image URL in response: {data}")

        except Exception as e:
            return ImageGenerationResult(success=False, error=str(e))
