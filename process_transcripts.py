import csv
import json
import os
import re

INPUT_FILE = "data/stream_capture/transcript_log.txt"
OUTPUT_DIR = "data/processed"
SONGS_CSV = os.path.join(OUTPUT_DIR, "songs_played.csv")
CONTINUITY_LOG = os.path.join(OUTPUT_DIR, "broadcast_continuity.txt")

from core_utils.ontology_manager import OntologyManager


def parse_log_line(line):
    """
    Extracts the timestamp and the JSON content from a log line.
    Handles both single JSON objects and Lists of JSON objects.
    """
    # Regex to find the leading timestamp [HH:MM:SS]
    match = re.match(r"^\[(\d{2}:\d{2}:\d{2})\]\s*(.*)", line.strip())
    if not match:
        return None, None

    timestamp = match.group(1)
    content_str = match.group(2)

    try:
        # Attempt to parse the content as JSON
        data = json.loads(content_str)
        return timestamp, data
    except params:
        # If simple parsing fails, it might be a multi-line JSON chunk
        # that got flattened or weirdly formatted. For now we assume the file
        # structure we saw earlier, which seemed valid per line or block.
        # However, looking at the previous file view, the file is actually
        # NOT one valid JSON per line. It has multi-line JSONs.
        # This function might need to change strategy: Read the whole file
        # and split by the timestamp pattern.
        return None, None

def parse_full_file(filepath):
    """
    Reads the entire file and splits it by the timestamp pattern `[HH:MM:SS]`.
    Returns a list of (timestamp, json_data) tuples.
    """
    with open(filepath, encoding='utf-8') as f:
        content = f.read()

    # Split by the timestamp pattern, but keep the delimiter
    # Pattern: a newline followed by [HH:MM:SS] OR start of file [HH:MM:SS]
    # We'll use a regex to accept the whole file and find iter matches
    pattern = re.compile(r"\[(\d{2}:\d{2}:\d{2})\]")

    parts = []
    last_pos = 0
    timestamps = []

    for match in pattern.finditer(content):
        # The content valid for the *previous* timestamp is between last_pos and match.start()
        # BUT the file starts with a timestamp.

        if match.start() > 0:
            # We have content from the previous match
            segment = content[last_pos:match.start()].strip()
            # The timestamp for this segment was stored in the previous iteration
            if timestamps:
                parts.append((timestamps[-1], segment))

        timestamps.append(match.group(1))
        # The content for *this* timestamp starts after the match
        last_pos = match.end()

    # Add the final segment
    if last_pos < len(content) and timestamps:
        segment = content[last_pos:].strip()
        parts.append((timestamps[-1], segment))

    parsed_entries = []
    for ts, raw_json in parts:
        try:
            # Clean up potential messiness
            if not raw_json: continue
            data = json.loads(raw_json)
            parsed_entries.append((ts, data))
        except json.JSONDecodeError:
            print(f"Failed to parse JSON for {ts}: {raw_json[:50]}...")

    return parsed_entries

def process_data(entries):
    songs = []
    continuity_events = []

    for ts, data in entries:
        # Data can be a dict or a list of dicts
        items = data if isinstance(data, list) else [data]

        for item in items:
            seg_type = item.get("segment_type")
            transcript = item.get("transcript")
            song_info = item.get("song_info")
            notes = item.get("notes")

            # --- Song Logic ---
            if song_info and song_info != "Unknown":
                # Clean up "Artist - Title"
                if " - " in song_info:
                    artist, title = song_info.split(" - ", 1)
                else:
                    artist = "Unknown"
                    title = song_info

                songs.append({
                    "timestamp": ts,
                    "artist": artist.strip(),
                    "title": title.strip(),
                    "raw_info": song_info
                })

            # --- Continuity Logic ---
            # We want to capture the flow: Time -- Speech -- Song
            event = {
                "timestamp": ts,
                "type": seg_type,
                "transcript": transcript,
                "song_info": song_info,
                "notes": notes
            }
            continuity_events.append(event)

    return songs, continuity_events

def write_outputs(songs, continuity):
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    # 1. Write Songs CSV
    with open(SONGS_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "artist", "title", "raw_info"])
        writer.writeheader()
        writer.writerows(songs)
    print(f"Written {len(songs)} songs to {SONGS_CSV}")

    # 2. Write Continuity Log
    ontology_mgr = OntologyManager()

    with open(CONTINUITY_LOG, 'w', encoding='utf-8') as f:
        f.write("BACKLINK BROADCAST CONTINUITY LOG\n")
        f.write("=================================\n\n")


        for event in continuity:
            ts = event['timestamp']

            # Formatting the block
            f.write(f"[{ts}]\n")

            if event['transcript']:
                # Validate Text
                try:
                    # Set ontology context based on timestamp hour
                    hour = int(ts.split(':')[0])
                    ontology_mgr.get_current_ontology(override_hour=hour)
                except Exception:
                    pass

                score = ontology_mgr.validate_text(event['transcript'], history=[])
                warning_flag = ""
                if score < 1.0:
                    warning_flag = " [⚠️ ONTO-VIOLATION]"

                f.write(f"  🎙️ DJ: \"{event['transcript']}\"{warning_flag}\n")

            if event['song_info']:
                f.write(f"  🎵 SONG: {event['song_info']}\n")

            if event['notes']:
                f.write(f"  📝 NOTE: {event['notes']}\n")

            f.write("\n" + "-"*40 + "\n\n")

    print(f"Written continuity log to {CONTINUITY_LOG}")


if __name__ == "__main__":
    print(f"Processing {INPUT_FILE}...")
    if not os.path.exists(INPUT_FILE):
        print("Input file not found!")
    else:
        entries = parse_full_file(INPUT_FILE)
        songs, continuity = process_data(entries)
        write_outputs(songs, continuity)
