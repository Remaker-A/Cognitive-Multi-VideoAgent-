import os
import httpx
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化配置
API_KEY = os.getenv("API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL", "MiniMax-M2.1")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.minimax.chat/v1")
TRUST_ENV = os.getenv("SOPHNET_TRUST_ENV", "").lower() in {"1", "true", "yes"}

# 初始化客户端
client = OpenAI(
    api_key=API_KEY,
    base_url=LLM_BASE_URL,
    http_client=httpx.Client(timeout=60.0, trust_env=TRUST_ENV),
)

# 测试调用
try:
    print(f"Testing with API_KEY: {API_KEY[:10]}...")
    print(f"Model: {CHAT_MODEL}")
    print(f"Base URL: {LLM_BASE_URL}")

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "system", "content": "你是一个专业的视频剧本作家"},
            {"role": "user", "content": "请为一个30秒的智能手表宣传视频创作一个简短的剧本大纲"}
        ],
    )
    
    print("\n✅ LLM API 连接成功！\n")
    print("生成的内容：")
    print("-" * 50)
    print(response.choices[0].message.content)
    print("-" * 50)
    
except Exception as e:
    print(f"\n❌ LLM API 连接失败: {e}")
