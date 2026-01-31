
import json
import os

LIBRARY_PATH = "../../honeycomb/aggregated_library.json"

def reset_unverified_plays():
    # Resolve path
    base_dir = os.path.dirname(__file__)
    file_path = os.path.abspath(os.path.join(base_dir, LIBRARY_PATH))

    print(f"📂 Opening Library: {file_path}")

    if not os.path.exists(file_path):
        print("❌ Library file not found.")
        return

    with open(file_path, encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("❌ Invalid JSON.")
            return

    count_modified = 0

    print(f"📊 Total Songs: {len(data)}")

    for song in data:
        # Check the condition: First played on Jan 18
        if song.get("first_played") == "2026-01-18" and song.get("plays", 0) != 0:
            song["plays"] = 0
            count_modified += 1

    # Save back
    if count_modified > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"✅ SUCCESS: Reset play counts to 0 for {count_modified} unverified songs (Imported Jan 18).")
    else:
        print("ℹ️ No songs found that matched criteria or they were already 0.")

if __name__ == "__main__":
    reset_unverified_plays()
