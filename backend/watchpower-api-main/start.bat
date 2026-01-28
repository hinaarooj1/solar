@echo off
echo Starting Solar Dashboard Backend...
echo ========================================

REM Check if .env exists
if not exist .env (
    echo WARNING: .env file not found!
    echo Create .env file with your configuration
    pause
    exit /b 1
)

REM Check Python
python --version

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt --quiet

REM Start the server
echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo Documentation at: http://localhost:8000/docs
echo ========================================

REM Use PORT env var if set, otherwise 8000
if "%PORT%"=="" set PORT=8000

python -m uvicorn fastapi_app:app --host 0.0.0.0 --port %PORT% --reload










