"""
测试 OmniMaaS 视频生成完整流程
"""
import os
import asyncio
import httpx
import time
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_video_generation_full():
    """测试完整的视频生成流程"""
    
    api_key = "sk-wyS2qftiByiBppuBLt9RmpdHRUezdhgzVNjqqfnR0uE"
    base_url = "https://api.omnimaas.com/v1"
    model = "sora-2"
    
    print(f"API Key: {api_key[:20]}...")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 步骤 1: 提交视频生成任务
    print("\n" + "="*80)
    print("步骤 1: 提交视频生成任务")
    print("="*80)
    
    try:
        async with httpx.AsyncClient(trust_env=False, timeout=60.0) as client:
            # 提交视频生成请求
            response = await client.post(
                f"{base_url}/videos",
                headers=headers,
                json={
                    "model": model,
                    "prompt": "A mouse runs toward the camera, smiling and blinking, cinematic quality, smooth motion",
                    "seconds": "4",  # 字符串类型
                    "size": "720x1280"
                }
            )
            
            print(f"状态码: {response.status_code}")
            print(f"响应: {response.text}")
            
            if response.status_code != 200:
                print(f"❌ 提交任务失败")
                return None
            
            task_data = response.json()
            task_id = task_data.get("id")
            status = task_data.get("status")
            
            print(f"\n✅ 任务提交成功!")
            print(f"  - 任务 ID: {task_id}")
            print(f"  - 状态: {status}")
            print(f"  - 时长: {task_data.get('seconds')}秒")
            print(f"  - 分辨率: {task_data.get('size')}")
            
            # 步骤 2: 轮询任务状态
            print("\n" + "="*80)
            print("步骤 2: 轮询任务状态")
            print("="*80)
            
            max_retries = 30  # 最多轮询 30 次
            retry_interval = 5  # 每次间隔 5 秒
            
            for i in range(max_retries):
                print(f"\n轮询 {i+1}/{max_retries}...")
                
                try:
                    response = await client.get(
                        f"{base_url}/videos/{task_id}",
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        task_data = response.json()
                        status = task_data.get("status")
                        progress = task_data.get("progress", 0)
                        
                        print(f"  状态: {status}")
                        print(f"  进度: {progress}%")
                        
                        if status in ["succeeded", "completed"]:
                            print(f"\n✅ 视频生成成功!")
                            
                            # 打印完整的任务数据
                            print(f"\n完整任务数据:")
                            import json
                            print(json.dumps(task_data, indent=2))
                            
                            # 获取视频 URL（尝试多个可能的字段名）
                            video_url = (
                                task_data.get("url") or 
                                task_data.get("video_url") or
                                task_data.get("output", {}).get("url") or
                                task_data.get("result", {}).get("url") or
                                task_data.get("data", {}).get("url")
                            )
                            
                            print(f"\n  - 视频 URL: {video_url}")
                            print(f"  - 时长: {task_data.get('seconds')}秒")
                            print(f"  - 分辨率: {task_data.get('size')}")
                            print(f"  - 创建时间: {task_data.get('created_at')}")
                            
                            return {
                                "success": True,
                                "task_id": task_id,
                                "status": status,
                                "video_url": video_url,
                                "task_data": task_data
                            }
                        
                        elif status == "failed":
                            error_msg = task_data.get("error", "Unknown error")
                            print(f"\n❌ 视频生成失败: {error_msg}")
                            return {
                                "success": False,
                                "task_id": task_id,
                                "status": status,
                                "error": error_msg,
                                "task_data": task_data
                            }
                        
                        elif status in ["queued", "processing", "in_progress"]:
                            print(f"  ⏳ 任务进行中...")
                            await asyncio.sleep(retry_interval)
                        
                        else:
                            print(f"  ❓ 未知状态: {status}")
                            await asyncio.sleep(retry_interval)
                    
                    else:
                        print(f"  ❌ 查询失败: {response.status_code}")
                        print(f"  响应: {response.text}")
                        await asyncio.sleep(retry_interval)
                
                except Exception as e:
                    print(f"  ❌ 查询出错: {str(e)}")
                    await asyncio.sleep(retry_interval)
            
            print(f"\n❌ 超时: 任务在 {max_retries * retry_interval} 秒内未完成")
            return {
                "success": False,
                "task_id": task_id,
                "status": "timeout",
                "error": f"Task timeout after {max_retries * retry_interval} seconds"
            }
    
    except Exception as e:
        print(f"\n❌ 错误: {str(e)}")
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    result = asyncio.run(test_video_generation_full())
    
    print("\n" + "="*80)
    print("最终结果")
    print("="*80)
    if result:
        if result.get("success"):
            print("✅ 视频生成成功!")
            print(f"视频 URL: {result.get('video_url')}")
        else:
            print(f"❌ 视频生成失败: {result.get('error')}")
    else:
        print("❌ 未返回结果")
