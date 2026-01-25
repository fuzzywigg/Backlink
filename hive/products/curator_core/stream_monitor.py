import time
import json
import os
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# --- CONFIGURATION ---
URL = "https://andonlabs.com/evals/radio"
LIBRARY_PATH = "../../honeycomb/aggregated_library.json"
CHECK_INTERVAL = 30 # Seconds

# Import Enricher (Assume same directory)
try:
    from enricher import MetadataEnricher
except ImportError:
    # Handle if running from root context
    import sys
    sys.path.append(os.path.dirname(__file__))
    from enricher import MetadataEnricher

class StreamMonitor:
    def __init__(self):
        self.enricher = MetadataEnricher()
        
        self.options = Options()
        self.options.add_argument("--headless")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        # Spoof User Agent
        self.options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
        
        self.library = self.load_library()
        self.known_titles = {item['title'].lower() for item in self.library}
        self.last_track_raw = ""

    def load_library(self):
        start_path = os.path.dirname(__file__)
        abs_path = os.path.abspath(os.path.join(start_path, LIBRARY_PATH))
        
        if not os.path.exists(abs_path):
            print(f"⚠️  LIBRARY NOT FOUND AT: {abs_path}")
            return []
            
        with open(abs_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_library(self):
        start_path = os.path.dirname(__file__)
        abs_path = os.path.abspath(os.path.join(start_path, LIBRARY_PATH))
        
        with open(abs_path, 'w', encoding='utf-8') as f:
            json.dump(self.library, f, indent=2)
            
    def sanitize_id(self, text):
        # Convert "Artist - Title" to "artist_title"
        clean = re.sub(r'[^a-zA-Z0-9\s]', '', text).lower()
        return clean.replace(' ', '_')

    def parse_station_blocks(self, full_text):
        """
        Parses the raw text to extract (Station Name, Song Title, Artist) tuples.
        Based on the layout:
        [Station Name]
        by [Model Name]
        NOW PLAYING
        LIVE
        [Song Title]
        [Artist] (Optional line)
        """
        stations_data = []
        
        # The text structure repeats. We can split by "Powered by Live365" which appears at the bottom of each card,
        # OR we can just look for the pattern "NOW PLAYING" and look backwards/forwards.
        
        # Let's try splitting by "Show More" or similar repeated footer to isolate cards.
        # "Powered by Live365" seems reliable as a delimiter.
        
        blocks = full_text.split("Powered by Live365")
        
        for block in blocks:
            lines = [l.strip() for l in block.split('\n') if l.strip()]
            if not lines: continue
            
            # Look for NOW PLAYING
            if "NOW PLAYING" not in lines:
                continue
                
            try:
                np_index = lines.index("NOW PLAYING")
                
                # STATION NAME is usually a few lines above "NOW PLAYING"
                if np_index >= 2:
                    station_name = lines[np_index-2]
                else:
                    station_name = "Unknown Station"
                
                # SONG INFO is below LIVE
                if "LIVE" in lines[np_index:]:
                    live_index = lines.index("LIVE", np_index)
                    if len(lines) > live_index + 1:
                        raw_title = lines[live_index + 1]
                        
                        # --- 1. Attempt Next Line Detection ---
                        raw_artist = "Unknown"
                        if len(lines) > live_index + 2:
                            next_line = lines[live_index + 2]
                            # Common pattern: "by Artist"
                            if next_line.lower().startswith("by "):
                                raw_artist = next_line[3:].strip() # remove "by "
                            # Heuristic: If it's not a UI element
                            elif "CURRENT" not in next_line and "POPULARITY" not in next_line:
                                raw_artist = next_line
                        
                        # --- 2. Attempt "Artist - Title" Split on Title ---
                        # Many streams use "Artist - Title" single line format
                        if raw_artist == "Unknown" or raw_artist == "":
                             # Check for hyphen separators
                            for sep in [" - ", " – ", " — "]:
                                if sep in raw_title:
                                    parts = raw_title.split(sep, 1) # Split only on first
                                    # Heuristic: Determine which is which. 
                                    # Usually "Artist - Title", but sometimes inverted.
                                    # We'll assume "Artist - Title" as standard for single-lines
                                    raw_artist = parts[0].strip()
                                    raw_title = parts[1].strip()
                                    break
                        
                        # --- 3. Attempt "Title by Artist" Split on Title ---
                        if " by " in raw_title and (raw_artist == "Unknown" or raw_artist == ""):
                            parts = raw_title.split(" by ")
                            raw_title = parts[0].strip()
                            raw_artist = parts[1].strip()

                        # --- DEBUG: Log if still Unknown ---
                        if raw_artist == "Unknown":
                            with open("parsing_failures.log", "a", encoding="utf-8") as f:
                                f.write(f"--- FAILURE {time.strftime('%H:%M:%S')} ---\n")
                                f.write(f"Raw Title: {raw_title}\n")
                                f.write("Block Context:\n")
                                f.write("\n".join(lines[np_index-2:live_index+4]))
                                f.write("\n----------------\n")

                        stations_data.append({
                            "station": station_name,
                            "title": raw_title,
                            "artist": raw_artist
                        })
            except Exception as e:
                print(f"⚠️ Parse Error in Block: {e}")
                
        return stations_data

    def run(self):
        print(f"🕵️  STREAM MONITOR V2: Watching {URL}")
        print(f"    Library Size: {len(self.library)} songs")
        
        driver = webdriver.Chrome(options=self.options)
        
        try:
            while True:
                driver.get(URL)
                time.sleep(5) # Wait for hydration
                
                body_text = driver.find_element(By.TAG_NAME, "body").text
                current_stations = self.parse_station_blocks(body_text)
                
                print(f"\n--- SCAN: {time.strftime('%H:%M:%S')} ---")
                
                for data in current_stations:
                    station_name = data['station']
                    title = data['title']
                    artist = data['artist']
                    
                    print(f"📻 {station_name}: {title} ({artist})")
                    
                    # ENRICH
                    enriched_data = None
                    genre = "Detected"
                    
                    full_query_id = self.sanitize_id(f"{artist}_{title}")
                    
                    # 2. CLASSIFICATION & STORAGE
                    # We distinguish between Validated Music and "DJ Content" (Speech, Ads, Hallucinations)
                    
                    is_music = False
                    if enriched_data:
                        is_music = True
                    elif title.lower() in self.known_titles:
                        is_music = True
                    
                    # Logic: If it's NOT in our library and Spotify doesn't know it -> It's likely a DJ Segment/Talk
                    
                    if is_music:
                        # --- MUSIC PATH ---
                        existing_entry = next((item for item in self.library if item["id"] == full_query_id), None)
                        
                        if existing_entry:
                            # Update Existing Song
                            if "stations" not in existing_entry: existing_entry["stations"] = []
                            if station_name not in existing_entry["stations"]:
                                existing_entry["stations"].append(station_name)
                                self.save_library()
                        else:
                            # Add New Song
                            new_entry = {
                                "id": full_query_id,
                                "title": title,
                                "artist": artist,
                                "genre": enriched_data.get('genre', 'Verified') if enriched_data else "Detected",
                                "plays": 1,
                                "source": "Stream_Monitor_V2",
                                "stations": [station_name],
                                "first_played": time.strftime("%Y-%m-%d"),
                                "last_played": time.strftime("%Y-%m-%d"),
                                # --- METADATA ENRICHMENT LAYER (Sovereign Inference) ---
                                "mood": "Analyzing...",
                                "energy_level": "Medium",
                                "bpm": "Unknown",
                                "era": "2020s",
                                "dj_tags": "New Arrival"
                            }
                            
                            # Heuristic Guessing based on Title/Artist keywords
                            inferred = self.infer_metadata(title, artist)
                            new_entry.update(inferred)
                            
                            if enriched_data:
                                new_entry.update({k:v for k,v in enriched_data.items() if k not in new_entry})
                                
                            self.library.append(new_entry)
                            self.known_titles.add(title.lower())
                            self.save_library()
                            print(f"   💾 SAVED MUSIC: {title} [Mood: {new_entry['mood']}]")
                            
                    else:
                        # --- DJ EVENTS PATH ---
                        # This captures: Talk radio, Station IDs, Hallucinations, Shoutouts
                        print(f"   🎙️  DJ SEGMENT DETECTED: {title} ({artist})")
                        self.log_dj_event({
                            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "station": station_name,
                            "raw_title": title,
                            "raw_artist": artist,
                            "type": self.classify_segment(title, artist)
                        })

                time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            print("\n🛑 Stopping Monitor.")
        except Exception as e:
            print(f"\n❌ CRITICAL ERROR: {e}")
        finally:
            driver.quit()

    def classify_segment(self, title, artist):
        # Heuristic classification for analysis
        text = f"{title} {artist}".lower()
        if "@" in text: return "SOCIAL_SHOUTOUT"
        if "call" in text or "dial" in text: return "CALL_TO_ACTION"
        if "http" in text or ".com" in text: return "URL_DROP"
        if "weather" in text or "traffic" in text: return "UTILITY"
        return "MONOLOGUE"

    def log_dj_event(self, event_data):
        log_path = os.path.join(os.path.dirname(__file__), "analytics", "dj_events.json")
        data = []
        if os.path.exists(log_path):
            with open(log_path, 'r') as f:
                try: data = json.load(f)
                except: pass
        
        # Dedupe mostly to avoid spamming the log with the same segment every 30s
        if data:
            last = data[-1]
            if last['station'] == event_data['station'] and last['raw_title'] == event_data['raw_title']:
                return # Skip duplicate polling
        
        data.append(event_data)
        with open(log_path, 'w') as f:
            json.dump(data, f, indent=2)

    def infer_metadata(self, title, artist):
        """
        Sovereign Heuristics for "Best Guess" Metadata tagging.
        """
        meta = {}
        t = title.lower()
        a = artist.lower()
        
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
        # Simple heuristic: If it looks like a remaster year, use that era
        if "202" in t: meta['era'] = "2020s"
        elif "201" in t: meta['era'] = "2010s"
        elif "199" in t: meta['era'] = "1990s"
        elif "198" in t: meta['era'] = "1980s"
        elif "197" in t: meta['era'] = "1970s"
        
        return meta

if __name__ == "__main__":
    bot = StreamMonitor()
    bot.run()
