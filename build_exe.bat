@echo off
setlocal
cd /d "%~dp0"

call venv\Scripts\activate.bat
pip install pyinstaller --quiet

pyinstaller --noconfirm --onedir --windowed --name JARVIS ^
    --add-data "config.yaml;." ^
    jarvis\app.py

echo.
echo Build complete. Find the app in dist\JARVIS\JARVIS.exe
endlocal
