@echo off
echo Starting Energy Dashboard Backend on port 8890...
cd /d "%~dp0"
python -m uvicorn api.main:app --reload --port 8890
pause
