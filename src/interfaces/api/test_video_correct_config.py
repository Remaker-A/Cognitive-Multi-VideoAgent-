"""
测试 OmniMaaS 视频生成 - 使用正确的配置
"""
import os
import asyncio
from openai import AsyncOpenAI
import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_video_generation():
    """测试视频生成"""
    
    # 使用正确的配置
    api_key = "sk-wyS2qftiByiBppuBLt9RmpdHRUezdhgzVNjqqfnR0uE"
    base_url = "https://api.omnimaas.com/v1"  # 正确的 base URL（不是 /videos）
    model = "sora-2"
    
    print(f"API Key: {api_key[:20]}...")
    print(f"Base URL: {base_url}")
    print(f"Model: {model}")
    
    # 初始化客户端（禁用代理）
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        http_client=httpx.AsyncClient(trust_env=False, timeout=600.0)
    )
    
    print("\n" + "="*80)
    print("测试视频生成")
    print("="*80)
    
    try:
        # 构建请求内容
        prompt = "A mouse runs toward the camera, smiling and blinking, cinematic quality, smooth motion"
        content = f"""Generate a video with the following specifications:

Prompt: {prompt}
Duration: 6 seconds
FPS: 24
Resolution: 1920x1080 (1080P)
Motion strength: 0.5

Please generate the video and return the video URL."""

        print(f"\n发送请求...")
        print(f"Prompt: {prompt[:100]}...")
        
        # 调用 API
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            max_tokens=1000
        )
        
        print(f"\n✅ 成功!")
        print(f"响应: {response.choices[0].message.content}")
        
        return {
            "success": True,
            "response": response.choices[0].message.content
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ 失败: {error_msg}")
        
        return {
            "success": False,
            "error": error_msg
        }

if __name__ == "__main__":
    asyncio.run(test_video_generation())
