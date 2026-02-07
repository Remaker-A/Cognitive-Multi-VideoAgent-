"""
测试 OmniMaaS API 连接
"""
import os
import asyncio
import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_connection():
    """测试 API 连接"""
    
    api_key = os.getenv("VIDEO_API_KEY")
    base_url = os.getenv("VIDEO_API_URL", "https://api.omnimaas.com/v1")
    
    print(f"API Key: {api_key[:20] if api_key else 'None'}...")
    print(f"Base URL: {base_url}")
    
    # 测试不同的 URL
    urls_to_test = [
        "https://api.omnimaas.com",
        "https://api.omnimaas.com/v1",
        "https://api.omnimaas.com/v1/models",
        "https://api.omnimaas.com/v1/chat/completions",
    ]
    
    # 测试不同的客户端配置
    configs = [
        ("默认配置", {}),
        ("信任环境变量", {"trust_env": True}),
        ("禁用代理", {"trust_env": False}),
        ("超时 30s", {"timeout": 30.0}),
        ("超时 60s", {"timeout": 60.0}),
    ]
    
    results = []
    
    for config_name, config in configs:
        print(f"\n{'='*80}")
        print(f"测试配置: {config_name}")
        print(f"{'='*80}")
        
        for url in urls_to_test:
            print(f"\n测试 URL: {url}")
            
            try:
                async with httpx.AsyncClient(**config) as client:
                    # 尝试 GET 请求
                    try:
                        response = await client.get(url, timeout=10.0)
                        print(f"  GET 请求: {response.status_code} - {response.reason_phrase}")
                        results.append((config_name, url, "GET", response.status_code, str(response.reason_phrase)))
                    except Exception as e:
                        print(f"  GET 请求失败: {str(e)[:100]}")
                        results.append((config_name, url, "GET", "Error", str(e)[:100]))
                    
                    # 尝试 POST 请求（带简单的测试数据）
                    try:
                        response = await client.post(
                            url,
                            json={"test": "connection"},
                            timeout=10.0
                        )
                        print(f"  POST 请求: {response.status_code} - {response.reason_phrase}")
                        results.append((config_name, url, "POST", response.status_code, str(response.reason_phrase)))
                    except Exception as e:
                        print(f"  POST 请求失败: {str(e)[:100]}")
                        results.append((config_name, url, "POST", "Error", str(e)[:100]))
            
            except Exception as e:
                print(f"配置错误: {str(e)[:100]}")
                results.append((config_name, "Config", "Error", "Error", str(e)[:100]))
    
    # 打印总结
    print(f"\n{'='*100}")
    print("测试总结")
    print(f"{'='*100}")
    print(f"{'配置':<20} {'URL':<40} {'方法':<10} {'状态':<15} {'信息'}")
    print(f"{'-'*100}")
    
    for config_name, url, method, status, info in results:
        url_short = url[:37] + "..." if len(url) > 37 else url
        status_str = str(status)
        info_short = info[:20] if info else ""
        print(f"{config_name:<20} {url_short:<40} {method:<10} {status_str:<15} {info_short}")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_connection())
