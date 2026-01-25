import json
from collections import defaultdict

INPUT_FILE = "hive/honeycomb/golden_history.json"
OUTPUT_FILE = "hive/honeycomb/aggregated_library.json"

def aggregate():
    print(f"📊 AGGREGATOR: Processing {INPUT_FILE}...")
    
    try:
        with open(INPUT_FILE, "r") as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print("❌ Input file not found.")
        return

    # Dictionary to hold unique songs
    library = {}

    for record in raw_data:
        song_id = record["id"]
        
        if song_id not in library:
            # First time seeing this song
            library[song_id] = {
                "id": song_id,
                "title": record["title"],
                "artist": record["artist"],
                "genre": record["genre"],
                "plays": 0,
                "source": "Curator_V1.2_Aggregation",
                "first_played": record.get("curated_at"),
                "last_played": record.get("curated_at") # Update this if we had timestamps
            }
        
        # Increment Play Count
        library[song_id]["plays"] += 1

    # Convert back to list
    final_list = list(library.values())
    
    # Sort by Plays (Descending)
    final_list.sort(key=lambda x: x["plays"], reverse=True)

    print(f"   Reduced {len(raw_data)} logs to {len(final_list)} unique songs.")
    
    with open(OUTPUT_FILE, "w") as f:
        json.dump(final_list, f, indent=2)
        
    print(f"✅ AGGREGATION COMPLETE: {OUTPUT_FILE}")

if __name__ == "__main__":
    aggregate()
