@echo off
title AI Hackathon Server
echo ====================================================
echo Starting AI Hackathon API Server...
echo Once started, keep this window OPEN.
echo Go to your browser and visit: http://127.0.0.1:8000
echo ====================================================
echo.
python -m uvicorn api:app --reload --host 127.0.0.1 --port 8000
pause
