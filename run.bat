@echo off
REM NewsTrader Startup Script for Windows

echo ================================================
echo     NewsTrader - AI-Powered Signal Generator
echo ================================================
echo.

REM Check if .env exists
if not exist .env (
    echo ERROR: .env file not found!
    echo.
    echo Please create .env file:
    echo   1. copy .env.example .env
    echo   2. Edit .env and add your API keys
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist venv (
    echo Warning: Virtual environment not found
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies if needed
python -c "import fastapi" 2>nul
if errorlevel 1 (
    echo Warning: Dependencies not installed
    echo Installing dependencies...
    pip install -r requirements.txt
    echo Dependencies installed
    echo.
)

REM Start the system
echo ================================================
echo Starting NewsTrader...
echo ================================================
echo.
echo API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop
echo.

python -m src.main --api
