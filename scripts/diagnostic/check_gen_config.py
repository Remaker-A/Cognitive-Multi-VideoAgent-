"""
Check image generator configuration
"""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv()

from src.interfaces.api.image_generator import ImageGenerator

print("Image Generator Configuration Check")
print("=" * 50)

# Create generator
gen = ImageGenerator()

print(f"Model: {gen.model}")
print(f"Base URL: {gen.base_url}")
print(f"API Key exists: {gen.api_key is not None}")
print(f"API Key length: {len(gen.api_key) if gen.api_key else 0}")
print(f"API Key starts with: {gen.api_key[:10] if gen.api_key else 'None'}...")

print("\nEnvironment Variables:")
print(f"IMAGE_MODEL: {os.getenv('IMAGE_MODEL')}")
print(f"IMAGE_API_URL: {os.getenv('IMAGE_API_URL')}")
print(f"IMAGE_API_KEY exists: {os.getenv('IMAGE_API_KEY') is not None}")

print("=" * 50)
print("Configuration looks OK!" if gen.api_key else "ERROR: No API key!")
