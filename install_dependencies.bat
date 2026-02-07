@echo off
echo Installing VideoGen performance optimization dependencies...
echo.

pip install transformers>=4.30.0
pip install torch>=2.0.0
pip install Pillow>=10.0.0
pip install opencv-python>=4.8.0
pip install aiohttp>=3.8.0
pip install aioboto3>=11.0.0
pip install requests>=2.31.0

echo.
echo Installation complete!
pause
