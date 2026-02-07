"""
测试 Gemini 3 Pro Image 生成功能
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from src.interfaces.api.image_generator import ImageGenerator


async def test_single_generation():
    """测试单张图像生成"""
    print("🚀 测试单张图像生成...")

    # 加载环境变量
    load_dotenv()

    try:
        # 创建生成器
        generator = ImageGenerator()

        # 测试 prompt
        prompt = "A beautiful sunset over mountains, digital art style"

        print(f"📝 Prompt: {prompt}")
        print(f"🔧 Model: {generator.model}")
        print(f"🌐 Base URL: {generator.base_url}")
        print(f"🔑 API Key: {generator.api_key[:20]}...")

        # 生成图像
        print("\n⏳ 正在生成图像...")
        result = await generator.generate(prompt)

        # 打印结果
        print("\n✅ 生成结果:")
        print(f"Success: {result.get('success')}")

        if result.get('success'):
            print(f"Image URL/Content: {str(result.get('image_url'))[:200]}...")
            print(f"Model: {result.get('model')}")
            print(f"Seed: {result.get('seed')}")

            # 打印原始响应（前500字符）
            if 'raw_response' in result:
                print(f"\n📦 Raw Response (前500字符):")
                print(str(result['raw_response'])[:500])
        else:
            print(f"❌ Error: {result.get('error')}")

        return result

    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主函数"""
    print("=" * 60)
    print("🎨 Gemini 3 Pro Image 生成测试")
    print("=" * 60)

    # 测试单张生成
    result = await test_single_generation()

    print("\n" + "=" * 60)
    if result and result.get('success'):
        print("✅ 测试完成!")
    else:
        print("❌ 测试失败!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
