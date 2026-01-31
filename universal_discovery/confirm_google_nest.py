import os
import sys

# Ensure we can import local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from universal_discovery.engine import DiscoveryEngine


def run():
    engine = DiscoveryEngine()
    engine.set_context("backlink_hive_scout")

    url = "https://support.google.com/googlenest/answer/9330256"

    scores = {"Strategic": 3, "Sovereign": 2, "Agentic": 5, "Technical": 5}

    print(f"Processing: {url}")
    entry = engine.save_review(
        url=url,
        name="Google Nest Support: Device Setup",
        summary="Official support page for Google Nest device setup. Pending review from dashboard.",
        analysis="Standard documentation. Likely useful for the 'Smart Home' aspect of the Backlink Hive but generic. Low priority.",
        rubric_scores=scores,
        update=True,
    )

    print("SUCCESS")
    print(entry)


if __name__ == "__main__":
    run()
