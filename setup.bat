@echo off
REM ============================================================
REM  Casper Personal Agent - Windows / Alienware setup
REM  Creates a virtual environment and installs dependencies.
REM  Run this ONCE. Afterwards use run.bat to start the agent.
REM ============================================================
setlocal

cd /d "%~dp0"

where py >nul 2>nul
if %errorlevel%==0 (
    set "PYLAUNCH=py -3"
) else (
    set "PYLAUNCH=python"
)

echo [1/3] Creating virtual environment (.venv) ...
%PYLAUNCH% -m venv .venv
if errorlevel 1 (
    echo ERROR: could not create the virtual environment. Is Python 3.11+ installed?
    exit /b 1
)

echo [2/3] Installing dependencies ...
call ".venv\Scripts\python.exe" -m pip install --upgrade pip
call ".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: dependency installation failed.
    exit /b 1
)

echo [3/3] Preparing .env ...
if not exist ".env" (
    copy ".env.example" ".env" >nul
    echo Created .env - open it and add your GOOGLE_API_KEY.
) else (
    echo .env already exists - leaving it untouched.
)

echo.
echo Setup complete. Edit .env to add your API key, then run: run.bat
endlocal
