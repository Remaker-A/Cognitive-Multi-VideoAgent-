"""
视频生成服务
封装 Wan2.2 视频生成 API 调用
"""

import httpx
import asyncio
import time
from typing import Optional, Dict, Any, List
from datetime import datetime

class VideoGenerator:
    """视频生成器"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://www.sophnet.com/api/open-apis/projects/easyllms/videogenerator/task"
        self.model = "Wan2.2-T2V-A14B"

    def _extract_task_id(self, data: Dict[str, Any]) -> Optional[str]:
        if not isinstance(data, dict):
            return None
        output = data.get("output", {})
        if isinstance(output, dict):
            return output.get("taskId") or output.get("task_id")
        return data.get("taskId") or data.get("task_id")

    def _extract_video_url(self, data: Dict[str, Any]) -> Optional[str]:
        if not isinstance(data, dict):
            return None
        output = data.get("output", {})
        if isinstance(output, dict):
            url = output.get("url") or output.get("video_url") or output.get("videoUrl")
            if url:
                return url
        content = data.get("content", {})
        if isinstance(content, dict):
            return content.get("video_url") or content.get("url") or content.get("videoUrl")
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
        poll_interval: float = 3.0,
        max_wait: float = 240.0
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

            video_url = self._extract_video_url(data)
            if status is None and video_url and "/None" not in video_url:
                return data

            await asyncio.sleep(poll_interval)

        return {"status": "TIMEOUT", "error": last_error or "timeout"}
    
    async def generate(
        self,
        description: str,
        size: str = "1280*720",
        watermark: bool = True,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        生成视频
        
        Args:
            description: 视频描述
            size: 视频尺寸
            watermark: 是否添加水印
            seed: 随机种子
            
        Returns:
            Dict: 包含 video_url 和其他信息
        """
        if seed is None:
            seed = int(datetime.now().timestamp()) % 10000
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.api_url,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "content": [
                            {
                                "type": "text",
                                "text": description
                            }
                        ],
                        "parameters": {
                            "size": size,
                            "watermark": watermark,
                            "seed": seed
                        }
                    }
                )
                
                if response.status_code != 200:
                    return {
                        "success": False,
                        "error": f"API returned {response.status_code}: {response.text}",
                        "description": description
                    }

                task_id = None
                result = None
                try:
                    result = response.json()
                    task_id = self._extract_task_id(result)
                except ValueError:
                    task_id = response.text.strip() or None

                video_url = self._extract_video_url(result) if result else None
                task_status = self._extract_task_status(result) if result else None

                if task_id and not video_url:
                    final_result = await self._poll_task(client, task_id)
                    task_status = self._extract_task_status(final_result) or task_status
                    video_url = self._extract_video_url(final_result) or video_url

                if not video_url:
                    return {
                        "success": False,
                        "error": "Video generation completed without video_url",
                        "description": description,
                        "task_id": task_id,
                        "task_status": task_status
                    }

                return {
                    "success": True,
                    "video_url": video_url,
                    "description": description,
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
                "description": description
            }
    
    async def generate_from_shots(
        self,
        shots: List[Dict[str, Any]],
        size: str = "1280*720"
    ) -> Dict[str, Any]:
        """
        从分镜脚本生成视频
        
        Args:
            shots: 分镜列表
            size: 视频尺寸
            
        Returns:
            Dict: 生成结果
        """
        # 合并所有镜头描述
        descriptions = [shot.get("description", "") for shot in shots]
        combined_description = " | ".join(descriptions)
        
        return await self.generate(
            description=combined_description,
            size=size
        )
