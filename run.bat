@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found at .venv\Scripts\python.exe
    echo Run this once first:
    echo     py -3.13 -m venv .venv
    echo     .venv\Scripts\python.exe -m pip install -r requirements.txt
    pause
    exit /b 1
)
".venv\Scripts\python.exe" web\main.py %*
if errorlevel 1 pause
endlocal
