@echo off
echo Starting VideoGen Server (FastAPI)...
set PYTHONPATH=%CD%
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
pause
