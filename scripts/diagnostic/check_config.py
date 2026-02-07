import os
from dotenv import load_dotenv

load_dotenv()

print("Image Generation Model Status Check")
print("=" * 50)
print(f"IMAGE_MODEL: {os.getenv('IMAGE_MODEL')}")
print(f"IMAGE_API_URL: {os.getenv('IMAGE_API_URL')}")
api_key = os.getenv('IMAGE_API_KEY', '')
print(f"IMAGE_API_KEY exists: {len(api_key) > 0}")
print(f"IMAGE_API_KEY length: {len(api_key)}")
print("=" * 50)
