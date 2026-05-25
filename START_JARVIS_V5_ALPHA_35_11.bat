@echo off
setlocal
cd /d %~dp0
python -m uvicorn jarvis_v5.app:app --reload --host 127.0.0.1 --port 8000
