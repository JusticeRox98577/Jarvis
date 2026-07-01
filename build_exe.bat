@echo off
setlocal
cd /d "%~dp0"

if not exist venv (
    echo No virtual environment found in this folder.
    echo Run run.bat first to set it up, then re-run build_exe.bat.
    echo.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

pip install pyinstaller --quiet

pyinstaller --noconfirm --onedir --windowed --name JARVIS --icon assets\jarvis.ico jarvis\app.py
if errorlevel 1 (
    echo.
    echo PyInstaller failed -- see the error output above.
    pause
    exit /b 1
)

echo [PACKAGE] Copying config.yaml and assets next to the exe...
copy /Y config.yaml dist\JARVIS\config.yaml >nul
xcopy /E /I /Y assets dist\JARVIS\assets >nul

echo.
echo Build complete: dist\JARVIS\JARVIS.exe
echo Run build_installer.bat next to produce a proper Setup.exe installer.
pause
endlocal
