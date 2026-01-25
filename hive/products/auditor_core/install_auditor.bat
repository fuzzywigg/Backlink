@echo off
echo [INSTALLER] Setting up The Auditor (Secrets Scanner)...

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.10+.
    pause
    exit /b
)

:: No external pip dependencies needed for basic regex scan!
echo [DEP] No external dependencies required.

:: Check for config
if not exist "auditor_config.json" (
    echo [WARNING] auditor_config.json missing. Defaults will be used.
)

echo [SUCCESS] Installation Complete.
echo [RUN] To scan this folder, run: python auditor.py
pause
