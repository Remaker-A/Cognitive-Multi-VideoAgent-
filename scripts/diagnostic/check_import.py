
import sys
import os
from dotenv import load_dotenv

# Simulate api_server path setup
sys.path.append(os.getcwd())
sys.path.append(os.path.join(os.getcwd(), 'src/interfaces/api'))

load_dotenv()

try:
    print(f"IMAGE_MODEL: {os.getenv('IMAGE_MODEL')}")
    from src.interfaces.api.image_generator import ImageGenerator
    
    gen = ImageGenerator()
    print(f"Generator Model: {gen.model}")
    
    if "qwen" in gen.model.lower():
        print("Attempting to import QwenAdapter...")
        from src.adapters.implementations import QwenAdapter
        print("Import successful")
        
        adapter = QwenAdapter(api_key=gen.api_key, base_url=gen.base_url)
        print(f"Adapter initialized: {adapter}")
    else:
        print("Not using Qwen model")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
