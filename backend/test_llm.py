# 测试 LLM API 连接
from openai import OpenAI

# 初始化客户端
client = OpenAI(
    api_key="HIqjkY_-k96vd-Hp_NxbhBb9fl6qLOgkzljWiWg7x7k8bb5d6wOIGj4YHLV8k_prEwM_e2VWRbxKx-_rLXJjwg",
    base_url="https://www.sophnet.com/api/open-apis/v1"
)

# 测试调用
try:
    response = client.chat.completions.create(
        model="DeepSeek-V3.2",
        messages=[
            {"role": "system", "content": "你是一个专业的视频剧本作家"},
            {"role": "user", "content": "请为一个30秒的智能手表宣传视频创作一个简短的剧本大纲"}
        ]
    )
    
    print("✅ LLM API 连接成功！\n")
    print("生成的内容：")
    print("-" * 50)
    print(response.choices[0].message.content)
    print("-" * 50)
    
except Exception as e:
    print(f"❌ LLM API 连接失败: {e}")
