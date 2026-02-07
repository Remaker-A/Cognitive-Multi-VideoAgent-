"""
图像生成服务
使用 OpenAI SDK 调用 Gemini 3 Pro Image 模型
"""

import os
import re
import base64
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime
from openai import AsyncOpenAI


import httpx

class ImageGenerator:
    """图像生成器 - 使用 Gemini 3 Pro Image"""

    def __init__(self, api_key: Optional[str] = None):
        # 优先使用传入的 api_key，否则从环境变量读取
        self.api_key = api_key or os.getenv("IMAGE_API_KEY")
        self.base_url = os.getenv("IMAGE_API_URL", "https://api.omnimaas.com/v1")
        self.model = os.getenv("IMAGE_MODEL", "Qwen/Qwen-Image-2512")
        self.trust_env = os.getenv("SOPHNET_TRUST_ENV", "").lower() in {"1", "true", "yes"}

        # 初始化 OpenAI 客户端，启用代理支持
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            http_client=httpx.AsyncClient(trust_env=self.trust_env, timeout=120.0)
        )
        
        # Global semaphore for throttling (lazy initialized)
        self._sem = None
        # Default concurrency limit (can be overridden by env)
        self.concurrency_limit = int(os.getenv("IMAGE_GEN_CONCURRENCY", "2"))

    def _get_semaphore(self) -> asyncio.Semaphore:
        """Lazy load semaphore to ensure it's created in the correct loop context if needed"""
        if self._sem is None:
            self._sem = asyncio.Semaphore(self.concurrency_limit)
        return self._sem

    def _extract_base64_image(self, content: str) -> Optional[str]:
        """
        从返回的 content 中提取 base64 图像数据

        Args:
            content: API 返回的内容，格式如 ![image](data:image/jpeg;base64,...)

        Returns:
            base64 编码的图像数据，如果提取失败则返回 None
        """
        # 尝试匹配 data:image/xxx;base64,... 格式
        match = re.search(r'data:image/\w+;base64,(.+)', content)
        if match:
            return match.group(1)
        return None

    def save_base64_image(self, base64_data: str, output_path: str) -> bool:
        """
        保存 base64 编码的图像到文件

        Args:
            base64_data: base64 编码的图像数据
            output_path: 输出文件路径

        Returns:
            是否保存成功
        """
        try:
            # 解码 base64 数据
            image_bytes = base64.b64decode(base64_data)

            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

            # 保存到文件
            with open(output_path, 'wb') as f:
                f.write(image_bytes)

            return True
        except Exception as e:
            print(f"保存图像失败: {str(e)}")
            return False

    async def generate(
        self,
        prompt: str,
        size: str = "1328*1328",
        seed: Optional[int] = None,
        save_path: Optional[str] = None,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        生成图像 (带有重试机制)

        Args:
            prompt: 图像描述
            size: 图像尺寸
            seed: 随机种子
            save_path: 可选的保存路径
            max_retries: 最大重试次数 (默认 3)

        Returns:
            Dict: 包含 image_url 和其他信息
        """
        if seed is None:
            seed = int(datetime.now().timestamp()) % 10000

        last_error = None
        
        for attempt in range(max_retries):
            try:
                # Apply global throttling
                async with self._get_semaphore():
                    # Add small delay to stagger starts if multiple come at once
                    if attempt == 0:
                        request_delay = float(os.getenv("IMAGE_GEN_DELAY", "1.0"))
                        if request_delay > 0:
                            await asyncio.sleep(request_delay)

                    # Check for Qwen model
                    if "qwen" in self.model.lower():
                        from src.adapters.implementations import QwenAdapter
                        adapter = QwenAdapter(api_key=self.api_key, base_url=self.base_url)
                        
                        # Parse dimensions if needed, default to 1024
                        width = 1024
                        height = 1024
                        # Parse size string "1024*1024"
                        if size and "*" in size:
                            try:
                                w_str, h_str = size.split("*")
                                # For Qwen, enforce 1024x1024 or standard ratios to ensure stability
                                # 1328 might be causing timeouts or failures
                                target_w = int(w_str)
                                target_h = int(h_str)
                                if target_w == 1328 and target_h == 1328:
                                     width = 1024
                                     height = 1024
                                else:
                                     width = target_w
                                     height = target_h
                            except:
                                pass
                        
                        result = await adapter.generate(
                            prompt=prompt,
                            width=width,
                            height=height,
                            seed=seed
                        )
                        
                        if result.success:
                            # If save_path is provided, copy/move the file
                            saved = False
                        if save_path:
                            import shutil
                            try:
                                os.makedirs(os.path.dirname(save_path), exist_ok=True)
                                shutil.copy2(result.artifact_url, save_path)
                                saved = True
                            except Exception as e:
                                print(f"Failed to copy image to save_path: {e}")
                                
                        # Convert to base64 data URI for compatibility
                        try:
                            with open(result.artifact_url, "rb") as img_f:
                                img_bytes = img_f.read()
                                b64_str = base64.b64encode(img_bytes).decode('utf-8')
                                data_uri = f"data:image/png;base64,{b64_str}"
                        except Exception as e:
                            print(f"Failed to convert to base64: {e}")
                            data_uri = result.artifact_url # Fallback to path
                                
                        return {
                            "success": True,
                            "image_url": data_uri, # Data URI
                            "base64_data": b64_str, 
                            "saved": saved,
                            "save_path": save_path or result.artifact_url,
                            "prompt": prompt,
                            "size": size,
                            "seed": seed,
                            "model": self.model,
                            "cost": result.cost
                        }
                    else:
                        raise Exception(result.error)

                # Original Gemini/OpenAI Logic
                # 使用 OpenAI SDK 调用 Gemini 模型
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                )

                # 提取生成的内容
                if response.choices and len(response.choices) > 0:
                    content = response.choices[0].message.content

                    # Gemini 返回的是 base64 编码的图像数据
                    # 格式: ![image](data:image/jpeg;base64,...)
                    image_data = content
                    base64_data = None
                    clean_data_url = None

                    # 提取纯 base64 数据和完整的 data URL
                    if "data:image" in content:
                        # 提取完整的 data URL (data:image/xxx;base64,...)
                        data_url_match = re.search(r'(data:image/[^)]+)', content)
                        if data_url_match:
                            clean_data_url = data_url_match.group(1)
                        
                        # 提取纯 base64 数据
                        base64_data = self._extract_base64_image(content)

                    # 如果提供了保存路径，自动保存图像
                    saved = False
                    if save_path and base64_data:
                        saved = self.save_base64_image(base64_data, save_path)

                    return {
                        "success": True,
                        "image_url": clean_data_url or image_data,  # 优先返回纯净的 data URL
                        "base64_data": base64_data,  # 纯 base64 数据
                        "saved": saved,
                        "save_path": save_path if saved else None,
                        "prompt": prompt,
                        "size": size,
                        "seed": seed,
                        "model": self.model,
                        "raw_response": response.model_dump()
                    }
                else:
                    raise Exception("No response from model")
            
            except Exception as e:
                last_error = str(e)
                print(f"Generate attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1, 2, 4s
                    await asyncio.sleep(wait_time)
        
        return {
            "success": False,
            "error": f"Failed after {max_retries} attempts. Last error: {last_error}",
            "prompt": prompt
        }

    async def generate_batch(
        self,
        prompts: list,
        size: str = "1328*1328",
        base_seed: int = 42,
        save_dir: Optional[str] = None
    ) -> list:
        """
        批量生成图像 (并行处理)

        Args:
            prompts: 图像描述列表
            size: 图像尺寸
            base_seed: 基础随机种子
            save_dir: 可选的保存目录，如果提供则自动保存所有图像

        Returns:
            List[Dict]: 生成结果列表
        """
        import asyncio
        
        # Limit concurrency to avoid rate limits
        # Previous 5 was too high for some APIs (e.g. ModelScope)
        # Default to 2 to be safe but allow override
        concurrency_limit = int(os.getenv("IMAGE_GEN_CONCURRENCY", "2"))
        sem = asyncio.Semaphore(concurrency_limit)
        
        # Delay between starting requests to avoid bursts
        request_delay = float(os.getenv("IMAGE_GEN_DELAY", "1.0"))
        
        async def _generate_one(i, prompt):
            # Stagger start times
            if i > 0 and request_delay > 0:
                await asyncio.sleep(i * request_delay)
                
            async with sem:
                # 如果提供了保存目录，生成文件名
                save_path = None
                if save_dir:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    save_path = os.path.join(save_dir, f"image_{timestamp}_{i}.jpg")

                return await self.generate(
                    prompt=prompt,
                    size=size,
                    seed=base_seed + i,
                    save_path=save_path
                )

        tasks = [_generate_one(i, prompt) for i, prompt in enumerate(prompts)]
        results = await asyncio.gather(*tasks)
        return results
