@echo off
setlocal
cd /d "%~dp0"

call venv\Scripts\activate.bat
pip install pyinstaller --quiet

pyinstaller --noconfirm --onedir --windowed --name JARVIS --icon assets\jarvis.ico jarvis\app.py

echo [PACKAGE] Copying config.yaml and assets next to the exe...
copy /Y config.yaml dist\JARVIS\config.yaml >nul
xcopy /E /I /Y assets dist\JARVIS\assets >nul

echo.
echo Build complete: dist\JARVIS\JARVIS.exe
echo Run build_installer.bat next to produce a proper Setup.exe installer.
endlocal
