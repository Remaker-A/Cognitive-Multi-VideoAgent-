"""
简单的图像生成API测试
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("图像生成 API 测试")
print("=" * 60)

# 测试数据
test_data = {
    "project_id": "test_001",
    "shot": 1,
    "shot_info": {
        "scene": "A beautiful sunset over mountains",
        "camera": "远景",
        "angle": "平视",
        "emotion": "平静"
    }
}

print("\n发送请求到: http://localhost:8000/api/generate-image")
print(f"请求数据: {json.dumps(test_data, indent=2, ensure_ascii=False)}")

try:
    response = requests.post(
        "http://localhost:8000/api/generate-image",
        json=test_data,
        timeout=120
    )
    
    print(f"\n响应状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n✅ 图像生成成功!")
        print(f"Success: {result.get('success')}")
        print(f"Project ID: {result.get('project_id')}")
        print(f"Shot: {result.get('shot')}")
        
        if result.get('image_url'):
            image_url = result.get('image_url')
            print(f"Image URL 长度: {len(image_url)}")
            print(f"Image URL 前100字符: {image_url[:100]}")
    else:
        print(f"\n❌ 请求失败")
        print(f"响应内容: {response.text}")
        
except requests.exceptions.Timeout:
    print("\n❌ 请求超时")
except Exception as e:
    print(f"\n❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
