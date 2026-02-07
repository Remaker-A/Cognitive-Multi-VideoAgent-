"""
获取 OmniMaaS 可用模型列表
"""
import os
import asyncio
import httpx
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def get_models():
    """获取可用模型列表"""
    
    api_key = "sk-wyS2qftiByiBppuBLt9RmpdHRUezdhgzVNjqqfnR0uE"
    base_url = "https://api.omnimaas.com/v1"
    
    print(f"API Key: {api_key[:20]}...")
    print(f"Base URL: {base_url}")
    
    print("\n获取模型列表...")
    
    try:
        async with httpx.AsyncClient(trust_env=False, timeout=60.0) as client:
            response = await client.get(
                f"{base_url}/models",
                headers={
                    "Authorization": f"Bearer {api_key}"
                }
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("data", [])
                
                print(f"\n找到 {len(models)} 个模型:\n")
                print(f"{'模型 ID':<50} {'拥有者':<20} {'支持的端点类型'}")
                print(f"{'-'*100}")
                
                video_models = []
                
                for model in models:
                    model_id = model.get("id", "N/A")
                    owned_by = model.get("owned_by", "N/A")
                    endpoint_types = model.get("supported_endpoint_types", [])
                    
                    # 检查是否是视频模型
                    endpoint_str = ", ".join(endpoint_types)
                    is_video = any("video" in t.lower() for t in endpoint_types)
                    
                    if is_video or "video" in model_id.lower() or "sora" in model_id.lower():
                        video_models.append(model)
                        print(f"{model_id:<50} {owned_by:<20} {endpoint_str} ⭐")
                    else:
                        print(f"{model_id:<50} {owned_by:<20} {endpoint_str}")
                
                print(f"\n{'='*100}")
                print(f"找到 {len(video_models)} 个视频相关模型:")
                for model in video_models:
                    print(f"  - {model.get('id')}")
                
                return models
            else:
                print(f"错误: {response.text}")
                return None
                
    except Exception as e:
        print(f"错误: {str(e)}")
        return None

if __name__ == "__main__":
    asyncio.run(get_models())
