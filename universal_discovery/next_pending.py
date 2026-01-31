import os
import sys

# Ensure we can import local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from universal_discovery.engine import DiscoveryEngine


def process_queue():
    engine = DiscoveryEngine()

    # Force context to backlink_hive_scout because that's where the PENDING items are
    engine.set_context("backlink_hive_scout")

    pending = engine.get_pending_reviews()

    if not pending:
        print("✅ No pending items in 'backlink_hive_scout' queue.")
        return

    print(f"📊 Found {len(pending)} pending items to process.")
    print("---------------------------------------------------")

    for item in pending:
        url = item.get("url")
        name = item.get("name")
        print(f"\n🔎 Reviewing: {url}")

        # In a real autonomy loop, we would call the Browser Agent here.
        # But this script is for the AGENT (ME) to call.
        # I cannot interactively ask ME questions while running a subprocess.
        # So this script essentially just OUTPUTS the next item for me to work on.

        print(f"TITLE: {name}")
        print(f"Please run: /linkhelp {url}")
        print("...(Stopping here to let Agent process one by one)...")
        break

if __name__ == "__main__":
    process_queue()
