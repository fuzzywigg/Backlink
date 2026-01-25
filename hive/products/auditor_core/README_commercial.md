# THE AUDITOR: Sovereign Code Scanner

**Version 1.0 (Commercial Release)**

## "Don't let a commit cost you everything."

The Auditor is a lightweight, verifiable python script that scans your codebase for high-risk patterns *before* you push to GitHub. It was built after the Jan 17 Backlink Incident to prevent recurrence.

### Features

* **Zero-Dependency:** Runs on standard Python 3.
* **Configurable:** Define your own regex patterns in `auditor_config.json`.
* **Fast:** Scans thousands of files in seconds.
* **Safe:** Ignores `.git`, `node_modules`, and binary files automatically.

### Quick Start

1. **Install:** Run `install_auditor.bat`.
2. **Configure:** Edit `auditor_config.json` to add custom keys (e.g. your specific API tokens).
3. **Run:** `python auditor.py` in the root of the folder you want to scan.

### Default Patterns

* Ethereum Private Keys (Hex)
* RSA/PEM Keys
* OpenAI API Keys
* Google API Keys
* Slack Tokens
* AWS Access Keys

### Sovereignty Note

This tool performs all analysis LOCALLY. No code is sent to the cloud. You are in control.
