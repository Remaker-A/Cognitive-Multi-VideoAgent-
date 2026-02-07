"""
使用 OpenAI SDK 调用视频生成
"""
import os
import asyncio
from openai import AsyncOpenAI
import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_openai_sdk_video():
    """使用 OpenAI SDK 调用视频生成"""
    
    api_key = "sk-wyS2qftiByiBppuBLt9RmpdHRUezdhgzVNjqqfnR0uE"
    base_url = "https://api.omnimaas.com/v1"
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
    print("使用 OpenAI SDK 调用视频生成")
    print("="*80)
    
    try:
        # 尝试使用 chat.completions 接口
        print("\n尝试 1: chat.completions 接口")
        
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": "Generate a 4-second video of a mouse running toward the camera, smiling and blinking, cinematic quality, smooth motion"
                }
            ],
            max_tokens=1000
        )
        
        print(f"✅ 成功!")
        print(f"响应: {response.choices[0].message.content}")
        
        # 检查响应中是否包含视频 URL
        import json
        print(f"\n完整响应:")
        print(json.dumps(response.model_dump(), indent=2))
        
        return {
            "success": True,
            "response": response.choices[0].message.content,
            "full_response": response.model_dump()
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"\n❌ 失败: {error_msg}")
        
        return {
            "success": False,
            "error": error_msg
        }

if __name__ == "__main__":
    result = asyncio.run(test_openai_sdk_video())
    
    print("\n" + "="*80)
    print("最终结果")
    print("="*80)
    if result.get("success"):
        print("✅ 成功!")
        print(f"响应: {result.get('response')}")
    else:
        print(f"❌ 失败: {result.get('error')}")
