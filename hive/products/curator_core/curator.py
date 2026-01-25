import pandas as pd
import json
import os
import argparse

# --- CONFIGURATION ---
DEFAULT_SCHEMA = {
    "title": "string",
    "artist": "string",
    "genre": "string",
    "bpm": "integer", 
    "key": "string",
    "mood": "string"
}

class TheCurator:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.processed_count = 0
        self.errors = []

    def run(self):
        print(f"🧹 THE CURATOR: Ingesting {self.input_file}...")
        
        # 1. Ingest
        try:
            if self.input_file.endswith(".csv"):
                df = pd.read_csv(self.input_file)
            elif self.input_file.endswith(".json"):
                 df = pd.read_json(self.input_file)
            else:
                print("❌ Unsupported format. Use CSV or JSON.")
                return
        except Exception as e:
            print(f"❌ Read Error: {e}")
            return

        print(f"   Found {len(df)} raw records.")

        # 2. Sanitize & Normalize
        clean_data = []
        for index, row in df.iterrows():
            record = self.process_row(row)
            if record:
                clean_data.append(record)
            else:
                self.errors.append(index)

        # 3. Output
        print(f"   Successfully Cured: {len(clean_data)} records.")
        print(f"   Rejected: {len(self.errors)} records.")
        
        self.save_output(clean_data)

    def process_row(self, row):
        """
        The Core Logic: Cleaning & Normalization
        This is where the 'Secret Sauce' lives.
        """
        # Example Logic: Music Metadata Cleaning
        try:
            # Handle varied capitalization in headers
            row_lower = {k.lower(): v for k, v in row.items()}
            
            title = str(row_lower.get("title", row_lower.get("name", ""))).strip()
            artist = str(row_lower.get("artist", "")).strip()
            
            # Filter out "Unknown" or empty
            if not title or not artist or "unknown" in artist.lower():
                return None 

            # Deduplication ID
            id_str = f"{artist}_{title}".lower().replace(" ", "_")
            
            # Construct Golden Record
            return {
                "id": id_str,
                "title": title,
                "artist": artist,
                "genre": str(row_lower.get("genre", "Alternative")), # Default genre
                "source": "Backlink Radio History",
                "curated_at": "2026-01-18"
            }
        except Exception as e:
            print(f"Row Error: {e}")
            return None

    def save_output(self, data):
        try:
            with open(self.output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ GOLDEN DATASET SAVED to {self.output_file}")
            print(f"   (This intellectual property is now a sovereign asset.)")
        except Exception as e:
            print(f"❌ Save Failed: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="The Curator: Data Cleaning Agent")
    parser.add_argument("input", help="Path to raw CSV/JSON")
    parser.add_argument("output", help="Path to save Golden JSON")
    
    args = parser.parse_args()
    
    bot = TheCurator(args.input, args.output)
    bot.run()
