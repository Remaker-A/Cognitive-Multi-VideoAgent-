"""
测试不同的视频模型名称
"""
import os
import asyncio
from openai import AsyncOpenAI
import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_model_names():
    """测试不同的模型名称"""
    
    api_key = os.getenv("VIDEO_API_KEY")
    base_url = os.getenv("VIDEO_API_URL", "https://api.omnimaas.com/v1")
    
    if not api_key:
        print("❌ 错误: 未找到 VIDEO_API_KEY 环境变量")
        return []
    
    print(f"API Key: {api_key[:20]}...")
    print(f"Base URL: {base_url}")
    
    # 尝试不同的模型名称
    model_names = [
        "sora-2",
        "sora2",
        "sora",
        "runway-gen3",
        "runway",
        "minimax-hailuo-2.3",
        "minimaxhailuo2.3",
        "video-gen",
        "video-generation",
        "gemini-2-flash-video",
        "gemini-video",
        "gemini-3-pro-video",
        "gemini-3-pro-video-preview",
        "video-01",
        "video-01-live",
        "video-02",
        "video-02-live",
    ]
    
    client = AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        http_client=httpx.AsyncClient(trust_env=False, timeout=60.0)
    )
    
    results = []
    
    for model_name in model_names:
        print(f"\n{'='*60}")
        print(f"测试模型: {model_name}")
        print(f"{'='*60}")
        
        try:
            response = await client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": "Generate a 3-second video of a cat running"
                    }
                ],
                max_tokens=100
            )
            
            print(f"✅ 成功! 模型 {model_name} 可用")
            print(f"响应: {response.choices[0].message.content[:100] if response.choices else 'No content'}")
            results.append((model_name, "成功", None))
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 失败: {error_msg[:200]}")
            
            # 判断错误类型
            if "可用渠道不存在" in error_msg:
                results.append((model_name, "模型不存在", error_msg))
            elif "404" in error_msg or "not found" in error_msg.lower():
                results.append((model_name, "404 错误", error_msg))
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                results.append((model_name, "认证失败", error_msg))
            else:
                results.append((model_name, "其他错误", error_msg))
    
    # 打印总结
    print(f"\n{'='*80}")
    print("测试总结")
    print(f"{'='*80}")
    print(f"{'模型名称':<30} {'状态':<15} {'错误信息'}")
    print(f"{'-'*80}")
    
    for model_name, status, error in results:
        error_str = error[:40] if error else ""
        print(f"{model_name:<30} {status:<15} {error_str}")
    
    # 找出成功的模型
    successful_models = [m for m, s, _ in results if s == "成功"]
    if successful_models:
        print(f"\n✅ 可用的模型: {', '.join(successful_models)}")
    else:
        print(f"\n❌ 没有找到可用的模型")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_model_names())
