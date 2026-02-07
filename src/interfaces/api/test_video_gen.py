# Test video generation API
import os
import httpx
import asyncio
import time

# 从环境变量读取配置
API_KEY = os.getenv("API_KEY", "sk-api-3b6daAu9xcYh0a5pmR7b3x5Y9-nL1DwWfEPBF9Xe8YbhAIp6_s8shqM8fMw9diLu06wBoShD-pWtbYyXJPPMXh4yYmdKnuk1b_gJbCpTu2ekf2-dbiNaLS0")
VIDEO_MODEL = os.getenv("VIDEO_MODEL", "MiniMaxHailuo2.3")
API_URL = "https://www.sophnet.com/api/open-apis/projects/easyllms/videogenerator/task"

async def poll_video_task(task_id, headers, base_url, poll_interval=5, max_wait=600):
    """Poll video task status until completion or timeout."""
    status_urls = [
        f"{base_url}/{task_id}",
        f"{base_url}?task_id={task_id}",
        f"{base_url}?taskId={task_id}",
    ]
    status_url = None
    deadline = time.monotonic() + max_wait
    last_error = None

    async with httpx.AsyncClient(timeout=30.0) as client:
        while time.monotonic() < deadline:
            urls_to_try = [status_url] if status_url else status_urls
            response = None

            for url in urls_to_try:
                try:
                    response = await client.get(url, headers=headers)
                except Exception as e:
                    last_error = e
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

            status = (
                data.get("output", {}).get("taskStatus")
                or data.get("taskStatus")
                or data.get("status")
                or data.get("output", {}).get("status")
            )
            if status:
                print(f"Status: {status}")

            output = data.get("output", {})
            result_url = None
            has_results = False
            if isinstance(output, dict):
                result_url = output.get("url") or output.get("video_url") or output.get("videoUrl")
                has_results = bool(output.get("results"))

            if not result_url:
                content = data.get("content", {})
                if isinstance(content, dict):
                    result_url = content.get("video_url") or content.get("url") or content.get("videoUrl")

            status_upper = str(status).upper() if status else None
            if status_upper in {"SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}:
                return data
            if status_upper in {"FAILED", "ERROR", "CANCELLED", "CANCELED"}:
                return data

            if status is None and (result_url or has_results):
                return data

            await asyncio.sleep(poll_interval)

    return {"status": "TIMEOUT", "error": str(last_error) if last_error else "timeout"}

async def test_video_generation():
    """Test video generation API"""

    description = "Rotating shot, a kitten running on a meadow, professional photography, cinematic"

    print("Video API test")
    print(f"Description: {description}")

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": VIDEO_MODEL,
                    "content": [
                        {
                            "type": "text",
                            "text": description
                        }
                    ],
                    "parameters": {
                        "size": "1280*720",
                        "watermark": True,
                        "seed": 16
                    }
                }
            )

        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            task_id = None
            result = None
            try:
                result = response.json()
                task_id = (
                    result.get("output", {}).get("taskId")
                    or result.get("output", {}).get("task_id")
                    or result.get("taskId")
                    or result.get("task_id")
                )
            except ValueError:
                task_id = response.text.strip() or None

            print("Video generation OK")
            if result is not None:
                print(f"Full response: {result}")
            else:
                print(f"Response: {response.text.strip()}")

            if task_id:
                print(f"Task ID: {task_id}")
                print("Polling video task...")
                final_result = await poll_video_task(
                    task_id,
                    {
                        "Authorization": f"Bearer {API_KEY}",
                        "Content-Type": "application/json",
                    },
                    API_URL,
                )
                final_status = (
                    final_result.get("output", {}).get("taskStatus")
                    or final_result.get("taskStatus")
                    or final_result.get("status")
                    or final_result.get("output", {}).get("status")
                )
                if final_status:
                    print(f"Final status: {final_status}")
                print(f"Final response: {final_result}")
            else:
                print("No task ID returned; skip polling.")
        else:
            print("Video generation failed")
    except Exception as e:
        print(f"Error: {e}")
if __name__ == "__main__":
    asyncio.run(test_video_generation())
