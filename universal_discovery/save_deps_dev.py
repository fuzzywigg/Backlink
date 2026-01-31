import json
import subprocess
import sys

# Define the data
url = "https://github.com/google/deps.dev"
name = "deps.dev API"
summary = "API for querying dependency graphs, licenses, and security advisories for open source packages."
analysis = "Critical upstream data source for the Security Bee (Hive Immunity Sprint). Enables autonomous auditing of the Hive's software supply chain and 'Radioactive Content' checking via OpenSSF Scorecards."
scores = {"Strategic": 9, "Sovereign": 8, "Agentic": 10, "Technical": 9}
context = "backlink_hive_scout"
status = "INTEGRATE"

# Construct command
cmd = [
    sys.executable,
    "universal_discovery/save_record.py",
    "--url", url,
    "--name", name,
    "--summary", summary,
    "--analysis", analysis,
    "--scores", json.dumps(scores),
    "--context", context,
    "--status", status
]

# Run
subprocess.run(cmd)
