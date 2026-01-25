@echo off
TITLE THE HONEYCOMB: DECOY SYSTEM INSTALLER
COLOR 0E

ECHO ===================================================
ECHO   THE HONEYCOMB
ECHO   Active Decoy Defense System
ECHO ===================================================
ECHO.
ECHO   [1] Installing Dependencies...
pip install web3 >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    ECHO   [ERROR] Python/Pip not found.
    PAUSE
    EXIT /B
)

ECHO   [2] Configuring Tripwires...
IF NOT EXIST "honeycomb_config.json" (
    ECHO   [INIT] Creating Default Config...
    python -c "import honeycomb_core; honeycomb_core.Honeycomb().load_config()"
    ECHO   [NOTE] Please edit 'honeycomb_config.json' to set your BAIT addresses!
    start notepad honeycomb_config.json
    PAUSE
)

ECHO   [3] Arming System...
start "THE HONEYCOMB - ARMED" python honeycomb_core.py

ECHO.
ECHO   [SUCCESS] Honeycomb is Active.
ECHO   Do not touch the Bait Wallets. If they move, you are compromised.
PAUSE
