@echo off
echo ==================================================
echo      THE CURATOR: MONITOR & ANALYTICS
echo ==================================================
echo.
echo [INFO] Step 1: Launching Stream Monitor (Continuous Capture)
echo        - Hits Live365 for Real-Time Data
echo        - Filters Music -> Library
echo        - Filters Speech -> Analytics Log
@echo off
start "THE MONITOR" cmd /k "python hive/products/curator_core/stream_monitor.py"
start "THE PROFILER" cmd /k "python hive/products/curator_core/analytics/profiler.py"
start "THE PUBLISHER" cmd /k "python hive/products/curator_core/publisher.py"

echo.
echo ==================================================
echo      DJ PROFILER (8-Hour Reporter)
echo ==================================================
echo.
echo [INFO] Step 2: Running Profiler Analysis
echo        - Reads 'dj_events.json'
echo        - Generates 'dj_analysis_profile.md'
echo.
:loop
echo [REPORTING] Generating Report at %TIME%...
python hive/products/curator_core/analytics/profiler.py
echo [SLEEP] Waiting 4 seconds (Testing Mode) - Normal is 8 Hours.
timeout /t 28800
goto loop
