@echo off
TITLE OPERATION v3: WATCHTOWER (SELF-EXTRACTING)
COLOR 0A

:: --- CONFIGURATION ---
SET "BASE_DIR=C:\Users\bomba\repos\Backlink"

ECHO ===================================================
ECHO   THE WATCHTOWER: STANDALONE DEPLOYMENT
ECHO ===================================================
ECHO   Target: %BASE_DIR%
ECHO.

:: 1. SETUP FOLDERS
IF NOT EXIST "%BASE_DIR%" (
    mkdir "%BASE_DIR%"
)
IF NOT EXIST "%BASE_DIR%\war_room" (
    mkdir "%BASE_DIR%\war_room"
)
CD /D "%BASE_DIR%"

:: 2. GENERATE HUNTER.PY (Surveillance Daemon)
ECHO [GENERATE] Writing hunter.py...
(
echo import time
echo import json
echo import os
echo from datetime import datetime
echo from web3 import Web3
echo.
echo RPC_URL = "https://eth.llamarpc.com"
echo LOG_FILE = "war_room/evidence_locker.json"
echo.
echo TARGETS = {
echo     "0x7aa67bFefb4FDafc779ff1843c6e3b3DfA0Af0a8": "SMTP.ETH (ZOMBIE)",
echo     "0x49F408664951b142b8cf955b2191f75737cE1960": "BOT_WALLET (BURNED)",
echo     "0x1cc87a77516f41f17f2d91c57dae1d00b263f2b0": "ATTACKER (TARGET)"
echo }
echo.
echo def log_event(event_type, details^):
echo     entry = { "timestamp": datetime.utcnow(^).isoformat(^), "type": event_type, "details": details }
echo     print(f"[{entry['timestamp']}] [ALERT] {event_type}: {details}"^)
echo     try:
echo         if os.path.exists(LOG_FILE^):
echo             with open(LOG_FILE, 'r'^) as f: data = json.load(f^)
echo         else: data = []
echo         data.append(entry^)
echo         with open(LOG_FILE, 'w'^) as f: json.dump(data, f, indent=2^)
echo     except: pass
echo.
echo def run_hunter(^):
echo     print("👁️ HUNTER ONLINE"^)
echo     w3 = Web3(Web3.HTTPProvider(RPC_URL^)^)
echo     if not w3.is_connected(^): return
echo     state = {}
echo     for addr in TARGETS:
echo         c = Web3.to_checksum_address(addr^)
echo         state[c] = { "bal": w3.eth.get_balance(c^), "nonce": w3.eth.get_transaction_count(c^) }
echo         print(f"Tracking: {TARGETS[addr]}"^)
echo     while True:
echo         try:
echo             for addr in TARGETS:
echo                 c = Web3.to_checksum_address(addr^)
echo                 name = TARGETS[addr]
echo                 n_bal = w3.eth.get_balance(c^)
echo                 if n_bal != state[c]["bal"]:
echo                     print(f"BALANCE CHANGE: {name}"^)
echo                     log_event("BALANCE", f"{name} changed"^)
echo                     state[c]["bal"] = n_bal
echo                 n_nonce = w3.eth.get_transaction_count(c^)
echo                 if n_nonce != state[c]["nonce"]:
echo                     print(f"TX DETECTED: {name}"^)
echo                     log_event("TX", f"{name} sent tx"^)
echo                     state[c]["nonce"] = n_nonce
echo             time.sleep(15^)
echo         except: time.sleep(5^)
echo if __name__ == "__main__": run_hunter(^)
) > hunter.py

:: 3. GENERATE HONEYPOT.PY (Trap)
ECHO [GENERATE] Writing honeypot.py...
(
echo import time
echo from web3 import Web3
echo RPC_URL = "https://zkevm-rpc.com"
echo TARGET = "0x49F408664951b142b8cf955b2191f75737cE1960"
echo def run_trap(^):
echo     print("🍯 HONEYPOT ACTIVE"^)
echo     w3 = Web3(Web3.HTTPProvider(RPC_URL^)^)
echo     if not w3.is_connected(^): return
echo     t = Web3.to_checksum_address(TARGET^)
echo     last_bal = w3.eth.get_balance(t^)
echo     print(f"Watching: {t}"^)
echo     while True:
echo         try:
echo             cur = w3.eth.get_balance(t^)
echo             if cur ^> last_bal:
echo                 print("\n🚨 ALERT: GAS INJECTED! TRAP TRIGGERED!"^)
echo                 last_bal = cur
echo             time.sleep(30^)
echo         except: time.sleep(30^)
echo if __name__ == "__main__": run_trap(^)
) > honeypot.py

:: 4. PATCH PATH
SET "PATH=%PATH%;C:\Users\bomba\AppData\Roaming\Python\Python313\Scripts"
SET "PATH=%PATH%;C:\Users\bomba\AppData\Roaming\Python\Python313"

:: 5. INSTALL LIBS
ECHO [INSTALL] Libraries...
pip install web3 requests >nul 2>&1

:: 6. LAUNCH
ECHO [LAUNCH] DAEMONS...
start "THE HUNTER" python hunter.py
start "THE HONEYPOT" python honeypot.py

ECHO [STATUS] DONE.
PAUSE
