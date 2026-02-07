"""
测试 Gemini 3 Pro Image 生成功能（带保存功能）
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 添加项目路径
sys.path.insert(0, os.path.dirname(__file__))

from src.interfaces.api.image_generator import ImageGenerator


async def test_with_save():
    """测试生成并保存图像"""
    print("🚀 测试生成并保存图像...")

    # 加载环境变量
    load_dotenv()

    try:
        # 创建生成器
        generator = ImageGenerator()

        # 测试 prompt
        prompt = "A beautiful sunset over mountains, digital art style"

        print(f"📝 Prompt: {prompt}")
        print(f"🔧 Model: {generator.model}")

        # 创建输出目录
        output_dir = "output_images"
        os.makedirs(output_dir, exist_ok=True)

        # 生成并保存图像
        save_path = os.path.join(output_dir, "test_image.jpg")
        print(f"\n⏳ 正在生成图像并保存到: {save_path}")

        result = await generator.generate(prompt, save_path=save_path)

        # 打印结果
        print("\n✅ 生成结果:")
        print(f"Success: {result.get('success')}")

        if result.get('success'):
            print(f"Saved: {result.get('saved')}")
            print(f"Save Path: {result.get('save_path')}")
            print(f"Model: {result.get('model')}")
            print(f"Seed: {result.get('seed')}")

            if result.get('saved'):
                # 检查文件大小
                file_size = os.path.getsize(save_path)
                print(f"📁 文件大小: {file_size / 1024:.2f} KB")
        else:
            print(f"❌ Error: {result.get('error')}")

        return result

    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def test_batch_save():
    """测试批量生成并保存"""
    print("\n🚀 测试批量生成并保存...")

    # 加载环境变量
    load_dotenv()

    try:
        # 创建生成器
        generator = ImageGenerator()

        # 测试 prompts
        prompts = [
            "A cute cat playing with yarn",
            "A futuristic city at night"
        ]

        print(f"📝 Prompts: {len(prompts)} 个")

        # 创建输出目录
        output_dir = "output_images/batch"
        os.makedirs(output_dir, exist_ok=True)

        # 批量生成并保存
        print(f"\n⏳ 正在批量生成图像并保存到: {output_dir}")
        results = await generator.generate_batch(prompts, save_dir=output_dir)

        # 打印结果
        print("\n✅ 批量生成结果:")
        for i, result in enumerate(results):
            print(f"\n[{i+1}] {prompts[i]}")
            print(f"  Success: {result.get('success')}")
            if result.get('success'):
                print(f"  Saved: {result.get('saved')}")
                print(f"  Path: {result.get('save_path')}")
            else:
                print(f"  Error: {result.get('error')}")

        return results

    except Exception as e:
        print(f"\n❌ 发生错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主函数"""
    print("=" * 60)
    print("🎨 Gemini 3 Pro Image 生成测试（带保存功能）")
    print("=" * 60)

    # 测试单张生成并保存
    result1 = await test_with_save()

    # 测试批量生成并保存
    result2 = await test_batch_save()

    print("\n" + "=" * 60)
    if result1 and result1.get('success') and result2:
        print("✅ 所有测试完成!")
    else:
        print("❌ 部分测试失败!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
