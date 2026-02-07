"""
简化的豆包 DeepSeek-V3 API 测试
直接测试 API 调用，不依赖复杂的模块导入
"""
import asyncio
import aiohttp
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("LLM_BASE_URL") + "/responses"
MODEL = os.getenv("CHAT_MODEL")


async def test_doubao_api():
    """测试豆包 API 调用"""
    print("=" * 60)
    print("🚀 豆包 DeepSeek-V3 API 测试")
    print("=" * 60)

    print(f"\n📋 配置信息:")
    print(f"  - API Key: {API_KEY[:20]}...")
    print(f"  - Endpoint: {BASE_URL}")
    print(f"  - Model: {MODEL}")

    # 构建请求
    payload = {
        "model": MODEL,
        "stream": False,
        "input": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "你好，请用一句话介绍一下你自己"
                    }
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print("\n💬 发送测试消息...")
    print(f"  - 消息: {payload['input'][0]['content'][0]['text']}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                BASE_URL,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                print(f"\n📡 响应状态: {response.status}")

                response_data = await response.json()

                if response.status == 200:
                    print("\n✅ API 调用成功!")

                    # 打印响应数据
                    print(f"\n📝 响应内容:")
                    if "choices" in response_data and response_data["choices"]:
                        choice = response_data["choices"][0]
                        message = choice.get("message", {})
                        content = message.get("content", "")

                        print(f"  - Model: {response_data.get('model', MODEL)}")
                        print(f"  - Content: {content}")

                        if "usage" in response_data:
                            usage = response_data["usage"]
                            print(f"  - Tokens: {usage.get('total_tokens', 0)}")
                    else:
                        print(f"  - 完整响应: {response_data}")

                    return True
                else:
                    print(f"\n❌ API 调用失败!")
                    print(f"  - 状态码: {response.status}")
                    print(f"  - 响应: {response_data}")
                    return False

    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_requirement_parsing():
    """测试需求解析"""
    print("\n\n" + "=" * 60)
    print("🎬 测试需求解析功能")
    print("=" * 60)

    payload = {
        "model": MODEL,
        "stream": False,
        "input": [
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": "你是一个专业的视频需求分析助手。请分析用户的输入，提取关键信息，包括：主题、场景、情绪、风格等。"
                    }
                ]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "我想制作一个关于春天的短视频，画面要温暖明亮，配上轻快的音乐"
                    }
                ]
            }
        ]
    }

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    print("\n💬 发送需求解析请求...")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                BASE_URL,
                json=payload,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                response_data = await response.json()

                if response.status == 200:
                    print("\n✅ 需求解析成功!")

                    if "choices" in response_data and response_data["choices"]:
                        choice = response_data["choices"][0]
                        message = choice.get("message", {})
                        content = message.get("content", "")

                        print(f"\n📝 解析结果:")
                        print(content)

                    return True
                else:
                    print(f"\n❌ 需求解析失败!")
                    print(f"  - 响应: {response_data}")
                    return False

    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
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
    exit(0 if success else 1)
