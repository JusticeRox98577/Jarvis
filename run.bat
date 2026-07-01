@echo off
setlocal
cd /d "%~dp0"

git rev-parse --is-inside-work-tree >nul 2>&1
if not errorlevel 1 (
    echo [SETUP] Checking for updates...
    git pull origin main
)

if not exist venv (
    echo [SETUP] Creating virtual environment...
    py -3 -m venv venv
)

call venv\Scripts\activate.bat

echo [SETUP] Installing/updating dependencies...
pip install -r requirements.txt --quiet

echo [BOOT] Launching J.A.R.V.I.S. ...
python -m jarvis.app

endlocal
