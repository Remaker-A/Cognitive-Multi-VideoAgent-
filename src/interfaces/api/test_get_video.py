"""
测试获取视频文件
"""
import os
import asyncio
import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_get_video():
    """测试获取视频文件"""
    
    api_key = "sk-wyS2qftiByiBppuBLt9RmpdHRUezdhgzVNjqqfnR0uE"
    base_url = "https://api.omnimaas.com/v1"
    
    # 使用之前生成的任务 ID
    task_id = "video_697855387b0481909b11e9e61aa45d1209c75d3407caf945"
    
    print(f"API Key: {api_key[:20]}...")
    print(f"Base URL: {base_url}")
    print(f"Task ID: {task_id}")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # 尝试不同的方式获取视频
    urls_to_try = [
        f"{base_url}/videos/{task_id}",
        f"{base_url}/videos/{task_id}/download",
        f"{base_url}/videos/{task_id}/url",
        f"{base_url}/files/{task_id}",
        f"{base_url}/files/{task_id}/content",
    ]
    
    print("\n尝试获取视频文件...")
    
    for url in urls_to_try:
        print(f"\n{'='*80}")
        print(f"尝试 URL: {url}")
        print(f"{'='*80}")
        
        try:
            async with httpx.AsyncClient(trust_env=False, timeout=60.0) as client:
                response = await client.get(
                    url,
                    headers=headers,
                    follow_redirects=True
                )
                
                print(f"状态码: {response.status_code}")
                print(f"Content-Type: {response.headers.get('content-type', 'N/A')}")
                
                if response.status_code == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    if 'video' in content_type:
                        print(f"✅ 获取到视频文件!")
                        print(f"文件大小: {len(response.content)} bytes")
                        
                        # 保存视频文件
                        output_path = f"test_video_{task_id}.mp4"
                        with open(output_path, 'wb') as f:
                            f.write(response.content)
                        print(f"已保存到: {output_path}")
                        
                        return {
                            "success": True,
                            "url": url,
                            "file_path": output_path,
                            "size": len(response.content)
                        }
                    
                    elif 'application/json' in content_type:
                        print(f"响应内容: {response.text[:500]}")
                    else:
                        print(f"响应内容: {response.text[:200]}")
                else:
                    print(f"响应: {response.text[:200]}")
        
        except Exception as e:
            print(f"错误: {str(e)[:200]}")
    
    return {
        "success": False,
        "error": "无法获取视频文件"
    }

if __name__ == "__main__":
    result = asyncio.run(test_get_video())
    
    print("\n" + "="*80)
    print("最终结果")
    print("="*80)
    if result.get("success"):
        print(f"✅ 成功获取视频!")
        print(f"URL: {result.get('url')}")
        print(f"文件路径: {result.get('file_path')}")
        print(f"文件大小: {result.get('size')} bytes")
    else:
        print(f"❌ 失败: {result.get('error')}")
