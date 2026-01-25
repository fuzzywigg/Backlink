@echo off
echo ==================================================
echo      THE CURATOR: STREAM MONITOR
echo ==================================================
echo.
echo [INFO] This tool runs a headless browser to watch Andon Labs.
echo [INFO] It automatically adds new songs to 'aggregated_library.json'.
echo.
python hive/products/curator_core/stream_monitor.py
pause
