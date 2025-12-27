"""
快速 API 连接测试
测试所有 SophNet API 的连通性
"""

import requests
import json
import time

def poll_video_task(task_id, headers, base_url, poll_interval=5, max_wait=600):
    """轮询视频任务直到完成或超时。"""
    status_urls = [
        f"{base_url}/{task_id}",
        f"{base_url}?task_id={task_id}",
        f"{base_url}?taskId={task_id}",
    ]
    status_url = None
    start_time = time.time()
    last_error = None

    while time.time() - start_time < max_wait:
        urls_to_try = [status_url] if status_url else status_urls
        response = None

        for url in urls_to_try:
            try:
                response = requests.get(url, headers=headers, timeout=30)
            except Exception as e:
                last_error = e
                continue

            if response.status_code == 200:
                status_url = url
                break

            last_error = f"{response.status_code} {response.text[:200]}"

        if response is None or response.status_code != 200:
            print("状态查询失败，等待重试...")
            time.sleep(poll_interval)
            continue

        try:
            data = response.json()
        except ValueError:
            text = response.text.strip()
            print(f"状态响应(非JSON): {text[:200]}")
            return {"raw": text}

        status = (
            data.get("output", {}).get("taskStatus")
            or data.get("taskStatus")
            or data.get("status")
            or data.get("output", {}).get("status")
        )

        if status:
            print(f"当前状态: {status}")

        output = data.get("output", {})
        if isinstance(output, dict):
            result_url = output.get("url") or output.get("video_url") or output.get("videoUrl")
            has_results = bool(output.get("results"))
        else:
            result_url = None
            has_results = False

        if status:
            status_upper = str(status).upper()
            if status_upper in {"SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}:
                return data
            if status_upper in {"FAILED", "ERROR", "CANCELLED", "CANCELED"}:
                return data

        if result_url or has_results:
            return data

        time.sleep(poll_interval)

    return {"status": "TIMEOUT", "error": str(last_error) if last_error else "timeout"}

def poll_image_task(task_id, headers, base_url, poll_interval=5, max_wait=600):
    """轮询图像任务直到完成或超时。"""
    status_urls = [
        f"{base_url}/{task_id}",
        f"{base_url}?task_id={task_id}",
        f"{base_url}?taskId={task_id}",
    ]
    status_url = None
    start_time = time.time()
    last_error = None

    while time.time() - start_time < max_wait:
        urls_to_try = [status_url] if status_url else status_urls
        response = None

        for url in urls_to_try:
            try:
                response = requests.get(url, headers=headers, timeout=30)
            except Exception as e:
                last_error = e
                continue

            if response.status_code == 200:
                status_url = url
                break

            last_error = f"{response.status_code} {response.text[:200]}"

        if response is None or response.status_code != 200:
            print("状态查询失败，等待重试...")
            time.sleep(poll_interval)
            continue

        try:
            data = response.json()
        except ValueError:
            text = response.text.strip()
            print(f"状态响应(非JSON): {text[:200]}")
            return {"raw": text}

        status = (
            data.get("output", {}).get("taskStatus")
            or data.get("taskStatus")
            or data.get("status")
            or data.get("output", {}).get("status")
        )

        if status:
            print(f"当前状态: {status}")

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

        if status:
            status_upper = str(status).upper()
            if status_upper in {"SUCCEEDED", "SUCCESS", "COMPLETED", "DONE"}:
                return data
            if status_upper in {"FAILED", "ERROR", "CANCELLED", "CANCELED"}:
                return data

        if image_url or results:
            return data

        time.sleep(poll_interval)

    return {"status": "TIMEOUT", "error": str(last_error) if last_error else "timeout"}

print("=" * 60)
print("  SophNet API 连接测试")
print("=" * 60)

API_KEY = "HIqjkY_-k96vd-Hp_NxbhBb9fl6qLOgkzljWiWg7x7k8bb5d6wOIGj4YHLV8k_prEwM_e2VWRbxKx-_rLXJjwg"
VIDEO_API_URL = "https://www.sophnet.com/api/open-apis/projects/easyllms/videogenerator/task"

# 测试 1: LLM API
print("\n1️⃣  测试 LLM API (DeepSeek-V3.2)")
print("-" * 60)

try:
    response = requests.post(
        "https://www.sophnet.com/api/open-apis/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "DeepSeek-V3.2",
            "messages": [
                {"role": "system", "content": "你是一个测试助手"},
                {"role": "user", "content": "说'测试成功'"}
            ]
        },
        timeout=30
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
        print(f"✅ LLM API 正常")
        print(f"响应: {content[:100]}")
    else:
        print(f"❌ LLM API 失败")
        print(f"错误: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ 连接失败: {e}")

# 测试 2: 图像生成 API
print("\n2️⃣  测试图像生成 API (Qwen Image)")
print("-" * 60)

try:
    response = requests.post(
        "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator/task",
        headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "qwen-image",
            "input": {
                "prompt": "测试图像"
            },
            "parameters": {
                "size": "1328*1328",
                "seed": 42
            }
        },
        timeout=60
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 图像生成 API 正常")
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)[:200]}")

        task_id = (
            result.get("output", {}).get("taskId")
            or result.get("output", {}).get("task_id")
            or result.get("taskId")
            or result.get("task_id")
        )
        if task_id:
            print(f"任务 ID: {task_id}")
            print("开始轮询任务状态...")
            final_result = poll_image_task(
                task_id,
                {
                    "Authorization": f"Bearer {API_KEY}",
                    "Content-Type": "application/json",
                },
                "https://www.sophnet.com/api/open-apis/projects/easyllms/imagegenerator/task",
            )
            final_status = (
                final_result.get("output", {}).get("taskStatus")
                or final_result.get("taskStatus")
                or final_result.get("status")
                or final_result.get("output", {}).get("status")
            )
            if final_status:
                print(f"最终状态: {final_status}")
            print(f"最终响应: {json.dumps(final_result, indent=2, ensure_ascii=False)[:500]}")
        else:
            print("未获取到任务 ID，跳过轮询。")
    else:
        print(f"❌ 图像生成 API 失败")
        print(f"错误: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ 连接失败: {e}")

# 测试 3: 视频生成 API
print("\n3️⃣  测试视频生成 API (Wan2.2-T2V-A14B)")
print("-" * 60)

try:
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post(
        VIDEO_API_URL,
        headers=headers,
        json={
            "model": "Wan2.2-T2V-A14B",
            "content": [
                {
                    "type": "text",
                    "text": "测试视频"
                }
            ],
            "parameters": {
                "size": "1280*720",
                "watermark": True,
                "seed": 16
            }
        },
        timeout=90
    )
    
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        task_id = None
        try:
            result = response.json()
            response_preview = json.dumps(result, indent=2, ensure_ascii=False)[:200]
            task_id = (
                result.get("output", {}).get("taskId")
                or result.get("output", {}).get("task_id")
                or result.get("taskId")
                or result.get("task_id")
            )
        except ValueError:
            response_preview = response.text.strip()[:200]
            task_id = response.text.strip() or None

        print(f"✅ 视频生成 API 正常")
        print(f"响应: {response_preview}")

        if task_id:
            print(f"任务 ID: {task_id}")
            print("开始轮询任务状态...")
            final_result = poll_video_task(task_id, headers, VIDEO_API_URL)
            final_status = (
                final_result.get("output", {}).get("taskStatus")
                or final_result.get("taskStatus")
                or final_result.get("status")
                or final_result.get("output", {}).get("status")
            )
            if final_status:
                print(f"最终状态: {final_status}")
            print(f"最终响应: {json.dumps(final_result, indent=2, ensure_ascii=False)[:500]}")
        else:
            print("未获取到任务 ID，跳过轮询。")
    else:
        print(f"❌ 视频生成 API 失败")
        print(f"错误: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ 连接失败: {e}")

# 总结
print("\n" + "=" * 60)
print("  测试完成")
print("=" * 60)
print("\n如果所有测试都通过，说明 API 配置正确！")
print("如果遇到连接失败，请检查：")
print("  1. 网络连接是否正常")
print("  2. 是否需要配置代理")
print("  3. 防火墙是否允许访问")
print("  4. DNS 解析是否正常")
