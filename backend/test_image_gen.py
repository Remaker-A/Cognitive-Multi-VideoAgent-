# Test image generation API
import httpx
import asyncio
import time

API_KEY = "HIqjkY_-k96vd-Hp_NxbhBb9fl6qLOgkzljWiWg7x7k8bb5d6wOIGj4YHLV8k_prEwM_e2VWRbxKx-_rLXJjwg"
API_URL = "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator/task"

async def poll_image_task(task_id, headers, base_url, poll_interval=5, max_wait=600):
    """Poll image task status until completion or timeout."""
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
            image_url = None
            results = None
            if isinstance(output, dict):
                image_url = output.get("url") or output.get("image_url") or output.get("imageUrl")
                results = output.get("results")
                if not image_url and isinstance(results, list) and results:
                    first = results[0]
                    if isinstance(first, dict):
                        image_url = first.get("url") or first.get("image_url") or first.get("imageUrl")

            status_upper = str(status).upper() if status else None
            if status_upper in {"SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}:
                return data
            if status_upper in {"FAILED", "ERROR", "CANCELLED", "CANCELED"}:
                return data

            if status is None and (image_url or results):
                return data

            await asyncio.sleep(poll_interval)

    return {"status": "TIMEOUT", "error": str(last_error) if last_error else "timeout"}

async def test_image_generation():
    """Test image generation API"""

    prompt = "A cute kitten running on a meadow, professional photography, high resolution"

    print("Image API test")
    print(f"Prompt: {prompt}")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                API_URL,
                headers={
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "qwen-image",
                    "input": {
                        "prompt": prompt
                    },
                    "parameters": {
                        "size": "1328*1328",
                        "seed": 42
                    }
                }
            )

        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            result = response.json()
            print("Image generation OK")
            print(f"Full response: {result}")

            task_id = (
                result.get("output", {}).get("taskId")
                or result.get("output", {}).get("task_id")
                or result.get("taskId")
                or result.get("task_id")
            )
            if task_id:
                print(f"Task ID: {task_id}")
                print("Polling image task...")
                final_result = await poll_image_task(
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
            print("Image generation failed")
    except Exception as e:
        print(f"Error: {e}")
if __name__ == "__main__":
    asyncio.run(test_image_generation())
