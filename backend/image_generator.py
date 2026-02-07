"""
图像生成服务
封装 Qwen 图像生成 API 调用
"""

import httpx
import asyncio
import time
from typing import Optional, Dict, Any
from datetime import datetime

class ImageGenerator:
    """图像生成器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator/task"
        self.model = "qwen-image"

    def _extract_task_id(self, data: Dict[str, Any]) -> Optional[str]:
        if not isinstance(data, dict):
            return None
        output = data.get("output", {})
        if isinstance(output, dict):
            return output.get("taskId") or output.get("task_id")
        return data.get("taskId") or data.get("task_id")

    def _extract_image_url(self, data: Dict[str, Any]) -> Optional[str]:
        if not isinstance(data, dict):
            return None
        output = data.get("output", {})
        if isinstance(output, dict):
            url = output.get("url") or output.get("image_url") or output.get("imageUrl")
            if url:
                return url
            results = output.get("results")
            if isinstance(results, list) and results:
                first = results[0]
                if isinstance(first, dict):
                    return first.get("url") or first.get("image_url") or first.get("imageUrl")
        return None

    def _extract_task_status(self, data: Dict[str, Any]) -> Optional[str]:
        if not isinstance(data, dict):
            return None
        output = data.get("output", {})
        status = None
        if isinstance(output, dict):
            status = output.get("taskStatus") or output.get("status")
        return status or data.get("taskStatus") or data.get("status")

    async def _poll_task(
        self,
        client: httpx.AsyncClient,
        task_id: str,
        poll_interval: float = 2.0,
        max_wait: float = 120.0
    ) -> Dict[str, Any]:
        status_urls = [
            f"{self.api_url}/{task_id}",
            f"{self.api_url}?task_id={task_id}",
            f"{self.api_url}?taskId={task_id}",
        ]
        status_url = None
        deadline = time.monotonic() + max_wait
        last_error: Optional[str] = None

        while time.monotonic() < deadline:
            urls_to_try = [status_url] if status_url else status_urls
            response = None

            for url in urls_to_try:
                try:
                    response = await client.get(
                        url,
                        headers={"Authorization": f"Bearer {self.api_key}"},
                    )
                except Exception as e:
                    last_error = str(e)
                    continue

                if response.status_code == 200:
                    status_url = url
                    break

                last_error = f"{response.status_code} {response.text[:200]}"

            if response is None or response.status_code != 200:
                await asyncio.sleep(poll_interval)
                continue

            try:
                data = response.json()
            except ValueError:
                return {"raw": response.text.strip()}

            status = self._extract_task_status(data)
            if status:
                status_upper = str(status).upper()
                if status_upper in {"SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}:
                    return data
                if status_upper in {"FAILED", "ERROR", "CANCELLED", "CANCELED"}:
                    return data

            image_url = self._extract_image_url(data)
            if status is None and image_url:
                return data

            await asyncio.sleep(poll_interval)

        return {"status": "TIMEOUT", "error": last_error or "timeout"}
    
    async def generate(
        self,
        prompt: str,
        size: str = "1328*1328",
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        生成图像
        
        Args:
            prompt: 图像描述
            size: 图像尺寸
            seed: 随机种子
            
        Returns:
            Dict: 包含 image_url 和其他信息
        """
        if seed is None:
            seed = int(datetime.now().timestamp()) % 10000
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "input": {
                            "prompt": prompt
                        },
                        "parameters": {
                            "size": size,
                            "seed": seed
                        }
                    }
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"API returned {response.status_code}: {response.text}",
                        "prompt": prompt
                    }

                result = response.json()
                task_id = self._extract_task_id(result)
                image_url = self._extract_image_url(result)
                task_status = self._extract_task_status(result)

                if task_id and not image_url:
                    final_result = await self._poll_task(client, task_id)
                    task_status = self._extract_task_status(final_result) or task_status
                    image_url = self._extract_image_url(final_result) or image_url

                if not image_url:
                    return {
                        "success": False,
                        "error": "Image generation completed without image_url",
                        "prompt": prompt,
                        "task_id": task_id,
                        "task_status": task_status
                    }

                return {
                    "success": True,
                    "image_url": image_url,
                    "prompt": prompt,
                    "size": size,
                    "seed": seed,
                    "task_id": task_id,
                    "task_status": task_status,
                    "raw_response": result
                }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt
            }
    
    async def generate_batch(
        self,
        prompts: list,
        size: str = "1328*1328",
        base_seed: int = 42
    ) -> list:
        """
        批量生成图像
        
        Args:
            prompts: 图像描述列表
            size: 图像尺寸
            base_seed: 基础随机种子
            
        Returns:
            List[Dict]: 生成结果列表
        """
        results = []
        
        for i, prompt in enumerate(prompts):
            result = await self.generate(
                prompt=prompt,
                size=size,
                seed=base_seed + i
            )
            results.append(result)
        
        return results
