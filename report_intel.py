
import json
from pathlib import Path

def generate_intel_report():
    print("--- HIVE INTELLIGENCE REPORT ---")
    
    path = Path("hive/honeycomb/intel.json")
    if not path.exists():
        print("No intel.json found.")
        return

    with open(path, "r") as f:
        data = json.load(f)

    # 1. Listeners
    listeners = data.get("listeners", {}).get("known_nodes", {})
    print(f"\n🎧 LISTENER DATABASE")
    print(f"Total Tracked: {len(listeners)}")
    if not listeners:
        print("(No listener data recorded locally)")
    
    # 2. Trends / Locales
    trends = data.get("trends", {}).get("archive", [])
    venues = [t for t in trends if t.get("type") == "venue"]
    print(f"\n📍 GEOGRAPHIC INTEL")
    if venues:
        print(f"Tracked Venues: {len(venues)}")
        for v in venues[:3]:
            print(f"  - {v['title']} ({v.get('description', 'No Loc')})")
    else:
        print("(No geographic trend data)")

    # 3. Broadcast State
    state = data.get("broadcast_state", {})
    now_playing = state.get("now_playing", {}).get("title", "Unknown")
    print(f"\n📻 BROADCAST STATE")
    print(f"Now Playing: {now_playing}")
    queue = state.get("queue", [])
    print(f"Queue Length: {len(queue)}")
    if queue:
        print(f"Next Up: {[t.get('title') for t in queue[:3]]}")

    # 4. Treasury (Local Intel View)
    treasury = data.get("treasury", {})
    print(f"\n💰 TREASURY (Intel View)")
    print(f"Balance: {treasury.get('balance')} {treasury.get('currency')}")

if __name__ == "__main__":
    generate_intel_report()
