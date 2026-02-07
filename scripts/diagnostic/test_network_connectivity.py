"""
测试网络连通性和API端点可达性
"""

import asyncio
import httpx
import socket


async def test_dns_resolution(hostname):
    """测试DNS解析"""
    try:
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS解析成功: {hostname} -> {ip}")
        return True
    except Exception as e:
        print(f"❌ DNS解析失败: {hostname} - {str(e)}")
        return False


async def test_http_connectivity(url):
    """测试HTTP连接"""
    try:
        async with httpx.AsyncClient(timeout=30.0, trust_env=False, follow_redirects=True) as client:
            response = await client.get(url)
            print(f"✅ HTTP连接成功: {url} (状态码: {response.status_code})")
            return True
    except Exception as e:
        print(f"❌ HTTP连接失败: {url} - {str(e)}")
        return False


async def test_api_endpoint(url, api_key=None):
    """测试API端点"""
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0, trust_env=False) as client:
            response = await client.get(url, headers=headers)
            print(f"✅ API端点可访问: {url} (状态码: {response.status_code})")
            return True
    except Exception as e:
        print(f"❌ API端点不可访问: {url} - {str(e)}")
        return False


async def main():
    print("="*60)
    print("网络连通性测试")
    print("="*60)
    
    # 测试DNS解析
    print("\n--- DNS解析测试 ---")
    hosts = [
        "ark.cn-beijing.volces.com",
        "api.omnimaas.com",
        "api.minimax.chat"
    ]
    
    for host in hosts:
        await test_dns_resolution(host)
    
    # 测试HTTP连接
    print("\n--- HTTP连接测试 ---")
    urls = [
        "https://ark.cn-beijing.volces.com",
        "https://api.omnimaas.com",
        "https://api.minimax.chat"
    ]
    
    for url in urls:
        await test_http_connectivity(url)
    
    # 测试API端点
    print("\n--- API端点测试 ---")
    api_endpoints = [
        "https://ark.cn-beijing.volces.com/api/v3",
        "https://api.omnimaas.com/v1",
        "https://api.minimax.chat/v1"
    ]
    
    for endpoint in api_endpoints:
        await test_api_endpoint(endpoint)
    
    # 测试具体API路径
    print("\n--- 具体API路径测试 ---")
    specific_endpoints = [
        "https://ark.cn-beijing.volces.com/api/v3/models",
        "https://api.omnimaas.com/v1/models",
        "https://api.omnimaas.com/v1/videos"
    ]
    
    for endpoint in specific_endpoints:
        await test_api_endpoint(endpoint)
    
    print("\n" + "="*60)
    print("网络连通性测试完成")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
