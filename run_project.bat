@echo off
echo Starting VideoGen Project...

echo [1/2] Starting Backend Server...
start "VideoGen Backend" cmd /k "set PYTHONPATH=%CD% && python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload"

echo [2/2] Starting Frontend Dev Server...
start "VideoGen Frontend" cmd /k "cd web-new && npm run dev"

echo Waiting for servers to initialize...
timeout /t 5
start http://localhost:5173/

echo Project is running.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
