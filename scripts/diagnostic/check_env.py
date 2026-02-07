import os
from dotenv import load_dotenv

load_dotenv()

for key, value in os.environ.items():
    if "API" in key or "KEY" in key or "TOKEN" in key:
        # Mask the value for security but show prefix/suffix
        if len(value) > 8:
            masked = value[:4] + "..." + value[-4:]
        else:
            masked = "***"
        print(f"{key}: {masked}")
