"""
检查图像生成模型状态
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from src.interfaces.api.image_generator import ImageGenerator


async def check_status():
    """检查图像生成器状态"""
    print("=" * 60)
    print("🔍 图像生成模型状态检查")
    print("=" * 60)
    
    # 读取配置
    print("\n📋 当前配置:")
    print(f"  IMAGE_MODEL: {os.getenv('IMAGE_MODEL')}")
    print(f"  IMAGE_API_URL: {os.getenv('IMAGE_API_URL')}")
    api_key = os.getenv('IMAGE_API_KEY', '')
    print(f"  IMAGE_API_KEY: {api_key[:20]}...{api_key[-10:] if len(api_key) > 30 else ''}")
    
    # 创建生成器
    try:
        generator = ImageGenerator()
        print("\n✅ ImageGenerator 初始化成功")
        print(f"  模型: {generator.model}")
        print(f"  API URL: {generator.base_url}")
        print(f"  API Key 长度: {len(generator.api_key) if generator.api_key else 0}")
    except Exception as e:
        print(f"\n❌ ImageGenerator 初始化失败: {e}")
        return
    
    # 测试简单生成
    print("\n🧪 测试图像生成...")
    test_prompt = "A simple red circle on white background"
    print(f"  测试 Prompt: {test_prompt}")
    
    try:
        result = await generator.generate(prompt=test_prompt)
        
        print("\n📊 生成结果:")
        print(f"  Success: {result.get('success')}")
        
        if result.get('success'):
            print("  ✅ 图像生成成功!")
            print(f"  模型: {result.get('model')}")
            print(f"  Seed: {result.get('seed')}")
            
            # 检查返回的数据
            if result.get('base64_data'):
                print(f"  Base64 数据长度: {len(result.get('base64_data'))}")
            if result.get('image_url'):
                print(f"  Image URL 长度: {len(result.get('image_url'))}")
        else:
            print(f"  ❌ 生成失败: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ 测试过程出错:")
        print(f"  错误类型: {type(e).__name__}")
        print(f"  错误信息: {str(e)}")
        
        # 打印详细堆栈
        import traceback
        print("\n📜 详细错误堆栈:")
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("检查完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(check_status())
