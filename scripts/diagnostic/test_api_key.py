import os
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
CHAT_MODEL = os.getenv("CHAT_MODEL", "MiniMax-M2.1")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.minimax.chat/v1")
TRUST_ENV = os.getenv("SOPHNET_TRUST_ENV", "").lower() in {"1", "true", "yes"}


print(f"Testing with API_KEY: {API_KEY[:10]}...")
print(f"Model: {CHAT_MODEL}")
print(f"Base URL: {LLM_BASE_URL}")
print(f"Trust Env: {TRUST_ENV}")

client = OpenAI(
    api_key=API_KEY,
    base_url=LLM_BASE_URL,
    http_client=httpx.Client(timeout=60.0, trust_env=TRUST_ENV),
)

try:
    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=[
            {"role": "user", "content": "Hello, are you working?"}
        ],
    )
    print("✅ API Key is working!")
    print(f"Response: {response.choices[0].message.content}")
except Exception as e:
    print(f"❌ API Key test failed: {e}")
