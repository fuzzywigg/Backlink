import json
import csv
import difflib

LIBRARY_PATH = 'hive/honeycomb/aggregated_library.json'
LIBRARY_PATH = 'hive/honeycomb/aggregated_library.json'
CSV_PATH = '../andon-fm-metadata.csv'

def normalize(text):
    return str(text).lower().strip()

def infer_metadata(title, artist):
    """
    Sovereign Heuristics for "Best Guess" Metadata tagging.
    """
    meta = {
        'mood': "Analyzing...",
        'energy_level': "Medium",
        'bpm': "-",
        'era': "2020s",
        'dj_tags': "New Arrival",
        'lyrical_theme': "-"
    }
    t = str(title).lower()
    
    # 1. MOOD / ENERGY
    if any(x in t for x in ['remix', 'club', 'dance', 'mix', 'techno']):
        meta['mood'] = "Energetic"
        meta['energy_level'] = "High"
        meta['dj_tags'] = "Club Ready|Remix"
    elif any(x in t for x in ['acoustic', 'live', 'unplugged', 'piano']):
        meta['mood'] = "Intimate"
        meta['energy_level'] = "Low"
        meta['dj_tags'] = "Acoustic|Chill"
    elif any(x in t for x in ['lofi', 'sleep', 'relax', 'study']):
        meta['mood'] = "Relaxing"
        meta['energy_level'] = "Low"
        meta['dj_tags'] = "Background|Focus"
    
    # 2. ERA
    if "202" in t: meta['era'] = "2020s"
    elif "201" in t: meta['era'] = "2010s"
    elif "199" in t: meta['era'] = "1990s"
    elif "198" in t: meta['era'] = "1980s"
    elif "197" in t: meta['era'] = "1970s"
    
    return meta

def run():
    # 1. Load Library
    with open(LIBRARY_PATH, 'r', encoding='utf-8') as f:
        library = json.load(f)
    
    # 2. Load CSV
    metadata_map = {}
    try:
        with open(CSV_PATH, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = normalize(row['song_title'])
                metadata_map[key] = row
    except FileNotFoundError:
        print("⚠️ Warning: CSV not found. Proceeding with inference only.")

    # 3. Merge
    updated_count = 0
    for song in library:
        title_key = normalize(song.get('title', ''))
        
        # Try exact match
        match = metadata_map.get(title_key)
        
        # Fuzzy / Substring Match
        if not match:
            for csv_title, csv_data in metadata_map.items():
                if csv_title in title_key or title_key in csv_title:
                    lib_artist = normalize(song.get('artist', ''))
                    csv_artist = normalize(csv_data.get('artist', ''))
                    if lib_artist in csv_artist or csv_artist in lib_artist or 'unknown' in lib_artist:
                        match = csv_data
                        break 
        
        # APPLY DATA
        if match:
            song['secondary_genre'] = match.get('secondary_genres')
            song['mood'] = match.get('mood')
            song['energy_level'] = match.get('energy_level')
            song['lyrical_theme'] = match.get('lyrical_theme')
            song['year'] = match.get('year_released')
            song['era'] = match.get('era')
            song['bpm'] = match.get('bpm_range')
            song['notable_features'] = match.get('notable_features')
            song['dj_tags'] = match.get('dj_tags')
            
            if song.get('artist') == 'Unknown' and match.get('artist'):
                song['artist'] = match['artist']
            updated_count += 1
        
        # BACKFILL INFERENCE (If still missing data)
        if not song.get('mood') or song.get('mood') == "-":
            inferred = infer_metadata(song.get('title', ''), song.get('artist', ''))
            song.update({k:v for k,v in inferred.items() if not song.get(k)})
            updated_count += 1

    # 4. Save
    with open(LIBRARY_PATH, 'w', encoding='utf-8') as f:
        json.dump(library, f, indent=2)

    print(f"Updated {updated_count} songs with metadata (CSV + Inference).")

if __name__ == "__main__":
    run()
