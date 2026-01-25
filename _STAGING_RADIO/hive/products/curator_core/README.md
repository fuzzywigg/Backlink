# THE CURATOR: Stream Monitor

**Status:** BETA

The Curator now includes a live stream monitor that watches the Andon Labs radio page and records metadata changes to the local library.

## Features

* **Live Monitoring:** Headless browser watches `https://andonlabs.com/evals/radio`.
* **Auto-Ingest:** Detects "Now Playing" text changes.
* **Deduplication:** Checks against `aggregated_library.json` before adding.
* **Sanitization:** Converts raw text to ID-friendly formats.

## Usage

1. Run `run_monitor.bat`.
2. Leave the window open.
3. New songs will automatically appear in `hive/honeycomb/aggregated_library.json`.

## Configuration

Edit `stream_monitor.py` to change:

* `URL`: The target stream page.
* `CHECK_INTERVAL`: How often to look (default: 30s).
