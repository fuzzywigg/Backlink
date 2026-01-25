@echo off
echo ==================================================
echo      BACKLINK HIVE: NIGHT OPS COMMANDER
echo ==================================================
echo.
echo [TASK 1] Launching THE HUNTER (Surveillance)...
start "THE HUNTER" cmd /k "python hunter.py"

echo [TASK 2] Launching PAPER TRADER (Strategy Test)...
start "PAPER TRADER" cmd /k "python hive/products/proxy_core/night_strategy.py"

echo [TASK 3] Launching BEEHIVE (Memory Ingestion)...
echo NOTE: Ensure 'ollama serve' is running!
start "THE BEEHIVE" cmd /k "python hive/products/beehive/bee_memory.py"

echo.
echo ✅ NIGHT SHIFT STARTED.
echo    - Monitor the opened windows for activity.
echo    - Check 'hive/security/iron_dome/proposals' in the morning for simulated trades.
echo    - Check 'war_room/evidence_locker.json' for Hunter logs.
echo.
pause
