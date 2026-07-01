@echo off
setlocal
cd /d "%~dp0"

where ISCC >nul 2>&1
if errorlevel 1 (
    echo Inno Setup Compiler ^(ISCC.exe^) not found on PATH.
    echo.
    echo Install the free Inno Setup from https://jrsoftware.org/isdl.php
    echo Not every install adds ISCC to PATH automatically -- if this still
    echo fails after installing, either add its folder ^(typically
    echo C:\Program Files ^(x86^)\Inno Setup 6^) to your PATH and reopen this
    echo terminal, or just open installer.iss directly in the Inno Setup
    echo Compiler app and click Build/Compile instead of running this script.
    echo.
    pause
    exit /b 1
)

if not exist dist\JARVIS\JARVIS.exe (
    echo dist\JARVIS\JARVIS.exe not found -- run build_exe.bat first.
    echo.
    pause
    exit /b 1
)

ISCC installer.iss
if errorlevel 1 (
    echo.
    echo ISCC reported an error -- see the output above.
    pause
    exit /b 1
)

echo.
echo Installer built: installer_output\JARVIS-Setup.exe
pause
endlocal
