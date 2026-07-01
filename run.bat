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
    if errorlevel 1 (
        echo.
        echo Failed to create a virtual environment. Is Python 3.10+ installed
        echo and on PATH? Check with: py -3 --version
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

echo [SETUP] Installing/updating dependencies...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo.
    echo Dependency install failed -- see the error output above.
    pause
    exit /b 1
)

echo [BOOT] Launching J.A.R.V.I.S. ...
python -m jarvis.app
if errorlevel 1 (
    echo.
    echo J.A.R.V.I.S. exited with an error -- see the output above.
    pause
)

endlocal
