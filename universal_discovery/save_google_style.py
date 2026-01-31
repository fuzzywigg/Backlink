import json
import subprocess
import sys

# Define the data
url = "https://github.com/google/styleguide"
name = "Google Style Guides"
summary = "Official style guides for Google-originated open-source projects."
analysis = "Critical for standardizing the Hive's Python and JS codebases. Enforcing these styles ensures high readability for agents and humans."
scores = {"Strategic": 8, "Sovereign": 9, "Agentic": 10, "Technical": 9}
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
