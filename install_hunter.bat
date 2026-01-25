@echo off
echo [INSTALLER] Setting up The Hunter (Surveillance Daemon)...

:: Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed. Please install Python 3.10+.
    pause
    exit /b
)

:: Install Dependencies
echo [DEP] Installing Web3.py...
pip install web3

:: Create Default Config if missing
if not exist "hunter_config.json" (
    echo [CONFIG] Creating default hunter_config.json...
    (
        echo {
        echo   "rpc_url": "https://eth.llamarpc.com",
        echo   "targets": {
        echo     "0x0000000000000000000000000000000000000000": "Example Target"
        echo   },
        echo   "log_file": "hunter_log.json",
        echo   "scan_interval": 15
        echo }
    ) > hunter_config.json
)

echo [SUCCESS] Installation Complete.
echo [RUN] To start, run: python hunter.py
pause
