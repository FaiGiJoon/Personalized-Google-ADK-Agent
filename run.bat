@echo off
REM ============================================================
REM  Casper Personal Agent - Windows / Alienware launcher
REM  Starts the agent using the .venv created by setup.bat.
REM ============================================================
setlocal

cd /d "%~dp0"

REM Make sure the console can render UTF-8 (prompts use em-dashes etc.)
chcp 65001 >nul
set "PYTHONUTF8=1"

if not exist ".venv\Scripts\python.exe" (
    echo Virtual environment not found. Run setup.bat first.
    exit /b 1
)

".venv\Scripts\python.exe" main.py
endlocal
