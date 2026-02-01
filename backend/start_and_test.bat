@echo off
cd /d E:\ai编程实战营\tts\backend
echo Starting server...
start /B venv\Scripts\python.exe -m uvicorn src.main:app --host 0.0.0.0 --port 8000
timeout /t 5 /nobreak > nul
echo Testing routes...
curl -s http://localhost:8000/openapi.json | python -c "import sys, json; data = json.load(sys.stdin); print('\n'.join(data.get('paths', {}).keys()))"
