@echo off
setlocal
cd /d "%~dp0"

where ISCC >nul 2>&1
if errorlevel 1 (
    echo Inno Setup Compiler ^(ISCC.exe^) not found on PATH.
    echo Install the free Inno Setup from https://jrsoftware.org/isdl.php
    echo ^(default install adds ISCC to PATH^), or just open installer.iss
    echo in the Inno Setup Compiler app and click Build.
    exit /b 1
)

if not exist dist\JARVIS\JARVIS.exe (
    echo dist\JARVIS\JARVIS.exe not found -- run build_exe.bat first.
    exit /b 1
)

ISCC installer.iss
echo.
echo Installer built: installer_output\JARVIS-Setup.exe
endlocal
