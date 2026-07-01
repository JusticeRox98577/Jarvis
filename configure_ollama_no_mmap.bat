@echo off
setlocal
echo This sets OLLAMA_NO_MMAP=1 as a permanent Windows user environment
echo variable, so Ollama stops leaving model files cached in system RAM
echo after they've finished loading onto the GPU. No admin rights needed.
echo.

setx OLLAMA_NO_MMAP 1 >nul
if errorlevel 1 (
    echo Failed to set the environment variable.
    exit /b 1
)

echo Done: OLLAMA_NO_MMAP=1 is now set for your Windows user account.
echo.
echo IMPORTANT - this only affects processes started AFTER this change:
echo   1. Right-click the Ollama icon in your system tray and Quit.
echo   2. Relaunch Ollama from the Start Menu.
echo   3. If J.A.R.V.I.S. is open, close it and run run.bat again.
echo.
echo Model loads will take ~5-10 seconds longer, but system RAM usage
echo will drop back down once a model finishes loading onto the GPU.
echo.
echo To undo this later, run:  setx OLLAMA_NO_MMAP ""
endlocal
