"""
测试 OmniMaaS 不同的视频生成端点
"""
import os
import asyncio
import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_video_endpoints():
    """测试不同的视频生成端点"""
    
    api_key = "sk-wyS2qftiByiBppuBLt9RmpdHRUezdhgzVNjqqfnR0uE"
    base_url = "https://api.omnimaas.com/v1"
    
    print(f"API Key: {api_key[:20]}...")
    print(f"Base URL: {base_url}")
    
    # 测试不同的端点
    endpoints = [
        # OpenAI 兼容端点
        {
            "name": "Chat Completions",
            "url": f"{base_url}/chat/completions",
            "method": "POST",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            "body": {
                "model": "sora-2",
                "messages": [{"role": "user", "content": "Generate a video of a cat"}],
                "max_tokens": 1000
            }
        },
        # 可能的视频生成端点
        {
            "name": "Videos Generate",
            "url": f"{base_url}/videos/generate",
            "method": "POST",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            "body": {
                "model": "sora-2",
                "prompt": "Generate a video of a cat",
                "duration": 6,
                "resolution": "1080P"
            }
        },
        {
            "name": "Videos",
            "url": f"{base_url}/videos",
            "method": "POST",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            "body": {
                "model": "sora-2",
                "prompt": "Generate a video of a cat"
            }
        },
        {
            "name": "Video Generation",
            "url": f"{base_url}/video_generation",
            "method": "POST",
            "headers": {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            "body": {
                "model": "sora-2",
                "prompt": "Generate a video of a cat"
            }
        },
        # 尝试 GET 请求获取模型列表
        {
            "name": "Models List (GET)",
            "url": f"{base_url}/models",
            "method": "GET",
            "headers": {
                "Authorization": f"Bearer {api_key}"
            }
        },
    ]
    
    results = []
    
    for endpoint in endpoints:
        print(f"\n{'='*80}")
        print(f"测试端点: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")
        print(f"方法: {endpoint['method']}")
        print(f"{'='*80}")
        
        try:
            async with httpx.AsyncClient(trust_env=False, timeout=60.0) as client:
                if endpoint['method'] == "GET":
                    response = await client.get(
                        endpoint['url'],
                        headers=endpoint['headers']
                    )
                else:
                    response = await client.post(
                        endpoint['url'],
                        headers=endpoint['headers'],
                        json=endpoint['body']
                    )
                
                print(f"状态码: {response.status_code}")
                print(f"响应: {response.text[:500]}")
                
                results.append({
                    "name": endpoint['name'],
                    "url": endpoint['url'],
                    "status": response.status_code,
                    "response": response.text[:200]
                })
                
        except Exception as e:
            print(f"错误: {str(e)[:200]}")
            results.append({
                "name": endpoint['name'],
                "url": endpoint['url'],
                "status": "Error",
                "response": str(e)[:200]
            })
    
    # 打印总结
    print(f"\n{'='*100}")
    print("测试总结")
    print(f"{'='*100}")
    print(f"{'端点名称':<30} {'URL':<40} {'状态':<10} {'响应'}")
    print(f"{'-'*100}")
    
    for result in results:
        url_short = result['url'][:37] + "..." if len(result['url']) > 37 else result['url']
        status_str = str(result['status'])
        response_short = result['response'][:20] if result['response'] else ""
        print(f"{result['name']:<30} {url_short:<40} {status_str:<10} {response_short}")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_video_endpoints())
