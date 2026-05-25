@echo off
python -m uvicorn jarvis_v5.app:app --reload --host 127.0.0.1 --port 8000
