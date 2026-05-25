@echo off
setlocal
cd /d %~dp0
python -m uvicorn jarvis_v5.app:app --host 127.0.0.1 --port 8000
