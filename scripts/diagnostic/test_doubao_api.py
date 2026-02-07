"""
测试豆包 DeepSeek-V3 API 配置
"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agents.interaction.requirement_parser.deepseek_client import DeepSeekClient
from src.agents.interaction.requirement_parser.config import get_config


async def test_doubao_api():
    """测试豆包 API 调用"""
    print("🚀 开始测试豆包 DeepSeek-V3 API...")

    # 加载配置
    config = get_config(validate=False)
    print(f"\n📋 配置信息:")
    print(f"  - API Key: {config.deepseek_api_key[:20]}...")
    print(f"  - Endpoint: {config.deepseek_api_endpoint}")
    print(f"  - Model: {config.deepseek_model_name}")

    # 创建客户端
    client = DeepSeekClient()

    try:
        print("\n💬 发送测试消息...")

        # 测试简单对话
        messages = [
            {"role": "user", "content": "你好，请用一句话介绍一下你自己"}
        ]

        response = await client.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=100
        )

        print("\n✅ API 调用成功!")
        print(f"\n📝 响应内容:")
        print(f"  - Model: {response.model}")
        print(f"  - Tokens: {response.usage.total_tokens}")
        print(f"  - Content: {response.choices[0].message.content}")

        return True

    except Exception as e:
        print(f"\n❌ API 调用失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await client.close()


async def test_requirement_parsing():
    """测试需求解析功能"""
    print("\n\n🎬 测试需求解析功能...")

    client = DeepSeekClient()

    try:
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的视频需求分析助手。请分析用户的输入，提取关键信息。"
            },
            {
                "role": "user",
                "content": "我想制作一个关于春天的短视频，画面要温暖明亮，配上轻快的音乐"
            }
        ]

        response = await client.chat_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )

        print("\n✅ 需求解析成功!")
        print(f"\n📝 解析结果:")
        print(response.choices[0].message.content)

        return True

    except Exception as e:
        print(f"\n❌ 需求解析失败: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await client.close()


async def main():
    """主函数"""
    print("=" * 60)
    print("豆包 DeepSeek-V3 API 测试")
    print("=" * 60)

    # 测试基础 API 调用
    test1 = await test_doubao_api()

    # 测试需求解析
    test2 = await test_requirement_parsing()

    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"  - 基础 API 调用: {'✅ 通过' if test1 else '❌ 失败'}")
    print(f"  - 需求解析功能: {'✅ 通过' if test2 else '❌ 失败'}")
    print("=" * 60)

    return test1 and test2


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
