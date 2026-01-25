@echo off
TITLE THE WATCHTOWER: INSTALLER
COLOR 0A

ECHO ===================================================
ECHO   THE WATCHTOWER
ECHO   Sovereign Surveillance System
ECHO ===================================================
ECHO.
ECHO   [1] Installing Python Dependencies...
pip install web3 requests >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO   [ERROR] Python/Pip not found. Please install Python 3.10+
    PAUSE
    EXIT /B
)

ECHO   [2] Checking Configuration...
IF NOT EXIST "hunter_config.json" (
    ECHO   [INIT] Creating Default Config...
    copy hunter_config_template.json hunter_config.json >nul
    ECHO   [NOTE] Please edit 'hunter_config.json' to add your target wallets!
    start notepad hunter_config.json
    PAUSE
)

ECHO   [3] Launching The Hunter...
start "THE HUNTER - ACTIVE" python hunter_core.py

ECHO.
ECHO   [SUCCESS] Watchtower is Active.
ECHO   Logs are being saved to 'evidence_locker.json'.
PAUSE
