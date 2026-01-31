import json

INPUT_FILE = "hive/honeycomb/aggregated_library.json"
OUTPUT_FILE = "hive/stations/open_air/context_payload.md"

def generate_payload():
    print("📡 OpenAIR: Preparing Context Payload...")

    try:
        with open(INPUT_FILE) as f:
            library = json.load(f)
    except FileNotFoundError:
        print("❌ Aggregated Library not found!")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# THE GOLDEN ARCHIVE: BACKLINK RADIO HISTORY\n\n")
        f.write("| Artist | Title | Genre | Plays |\n")
        f.write("| :--- | :--- | :--- | :--- |\n")

        for song in library:
            artist = song.get("artist", "Unknown")
            title = song.get("title", "Unknown")
            genre = song.get("genre", "Unknown")
            plays = song.get("plays", 0)
            f.write(f"| {artist} | {title} | {genre} | {plays} |\n")

    print(f"✅ Payload Ready: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_payload()
