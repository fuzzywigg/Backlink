
import json
import logging
import random
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, List

from dotenv import load_dotenv
from google import genai
from google.genai import types

from hive.bees.base_bee import EmployedBee
from core_utils.ontology_manager import OntologyManager

# Configure Logging
logger = logging.getLogger("ConsultantBee")

class ConsultantBee(EmployedBee):
    """
    Simulates "Checking with other LLMs" (Grok, ChatGPT, etc.) via Gemini persona simulation.
    
    Responsibilities:
    1. Read the 'External' library (grok_playlist.json).
    2. Consult Gemini to select tracks that match the current station Vibe + Global Trends.
    3. 'Import' these tracks into the Hive Memory (intel.json) so the DJ can play them.
    """

    BEE_TYPE = "consultant"
    BEE_NAME = "Consultant Bee"
    CATEGORY = "research"

    def __init__(self, hive_path: str | None = None):
        super().__init__(hive_path)
        load_dotenv()
        self.ontology_manager = OntologyManager()
        
        # Initialize Gemini Client
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        print(f"DEBUG: Main Env Key found: {bool(api_key)}")
        
        if not api_key:
             try:
                 key_path = Path("hive/keys.json")
                 print(f"DEBUG: Checking {key_path.absolute()}")
                 if key_path.exists():
                     with open(key_path) as f:
                         data = json.load(f)
                         api_key = data.get("GEMINI_API_KEY") or data.get("GOOGLE_API_KEY")
                         print(f"DEBUG: Key loaded from file: {bool(api_key)}")
             except Exception as e:
                 print(f"DEBUG: Key load error: {e}")
        
        if api_key:
            try: 
                 self.client = genai.Client(api_key=api_key)
                 print("DEBUG: Client initialized.")
            except Exception as e:
                 print(f"DEBUG: Client init crashed: {e}")
                 self.client = None
        else:
            self.client = None

    def work(self, task: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Consults the 'Council of LLMs' to curate potential tracks.
        """
        self.log("Consultant Bee: convening the council for candidates...")
        
        # Determine batch size
        batch_size = 5
        if task and "batch_size" in task.get("payload", {}):
            batch_size = task["payload"]["batch_size"]
        
        # 1. Load External Library (Grok) as a SOURCE of inspiration
        grok_source = self._load_grok_library()
        
        # 2. Get Context (Vibe + Trends)
        ontology = self.ontology_manager.get_current_ontology()
        intel = self.read_intel()
        trends = intel.get("trends", {}).get("current", [])
        
        # 3. Consult LLM to pick CANDIDATES
        # We ask the LLM to pick songs that match the vibe, using Grok as a menu
        selected_candidates = self._consult_llm(grok_source, ontology, trends, batch_size)
        
        # 4. Sync to Intel (As Candidates)
        self._sync_candidates_to_hive_memory(selected_candidates)
        
        return {
            "status": "success", 
            "candidates_generated": len(selected_candidates),
            "candidates": selected_candidates
        }

    def _load_grok_library(self) -> List[dict]:
        """Loads the raw Grok playlist."""
        path = Path("grok_playlist.json")
        if not path.exists():
            return []
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return data.get("liked_songs", [])
        except Exception as e:
            self.log(f"Failed to read Grok library: {e}", level="error")
            return []

    def _consult_llm(self, library: List[dict], ontology: dict, trends: List[dict], limit: int) -> List[dict]:
        """
        Asks Gemini to act as a Music Curator picking candidates.
        """
        if not self.client:
            # Fallback: Random sample if no LLM
            return random.sample(library, min(limit, len(library))) if library else []

        # Use a large sample of the library to give the LLM options
        library_sample = library[:200] if library else []
        
        prompt = f"""
        You are the Head of Music Strategy for a radio station.
        
        CURRENT VIBE: {ontology.get('vibe')}
        
        TASK:
        Select {limit} songs that fit this vibe. 
        You can choose from the 'Source List' below OR suggest other songs that perfectly match the vibe.
        
        SOURCE LIST (Optional Inspiration):
        {json.dumps(library_sample)}
        
        OUTPUT:
        JSON list of track objects (keys: title, artist).
        DO NOT return marked-down code blocks. REMOVE ```json text.
        Add a 'reason' key explaining why it fits the vibe.
        """
        
        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)
            
        except Exception as e:
            self.log(f"Consultation failed: {e}", level="error")
            return random.sample(library, min(limit, len(library))) if library else []

    def _sync_candidates_to_hive_memory(self, tracks: List[dict]):
        """
        Updates intel.json 'music_library.candidates'.
        """
        intel = self.read_intel()
        
        if "music_library" not in intel:
            intel["music_library"] = {"owned": [], "rented": [], "candidates": []}
        
        if "candidates" not in intel["music_library"]:
            intel["music_library"]["candidates"] = []
            
        # Add new candidates
        for track in tracks:
            intel["music_library"]["candidates"].append({
                "title": track.get("title"),
                "artist": track.get("artist"),
                "source": "Consultant_Suggestion",
                "suggested_at": datetime.now(timezone.utc).isoformat(),
                "reason": track.get("reason", "Vibe Match")
            })
            
        # Write back
        target_path = Path("hive/honeycomb/intel.json")
        with open(target_path, 'w') as f:
            json.dump(intel, f, indent=2)

    def _sync_to_hive_memory(self, tracks: List[dict]):
        """
        Updates intel.json 'music_library.owned' so DJ can see them.
        """
        intel = self.read_intel()
        
        # Ensure structure exists
        if "music_library" not in intel:
            intel["music_library"] = {"owned": [], "rented": []}
        
        current_titles = {t["title"].lower() for t in intel["music_library"]["owned"]}
        
        added_count = 0
        for track in tracks:
            if track["title"].lower() not in current_titles:
                # Format for DJ Bee
                new_track = {
                    "id": f"grok_{random.randint(1000,9999)}",
                    "title": track.get("title"),
                    "artist": track.get("artist"),
                    "source": "Grok_Import",
                    "acquired_at": datetime.now(timezone.utc).isoformat(),
                    "vibe_match": track.get("reason", "Consultant Selection")
                }
                intel["music_library"]["owned"].append(new_track)
                added_count += 1
                
        if added_count > 0:
            self.log(f"Synced {added_count} new tracks from Grok to Hive Memory.")
            # Write back
            # Note: In a real concurrent swarm, we'd use a lock or atomic write. 
            # For this prototype, overwriting intel.json is the standard mechanic.
            target_path = Path("hive/honeycomb/intel.json")
            with open(target_path, 'w') as f:
                json.dump(intel, f, indent=2)
            
            # Update Public Site
            self._update_public_site(intel["music_library"]["owned"])

    def _update_public_site(self, tracks: List[dict]):
        """
        Regenerates public/songs.html with the latest inventory.
        """
        try:
            html_path = Path("public/songs.html")
            if not html_path.exists():
                return
                
            # Convert Hive tracks to UI format
            ui_tracks = []
            for t in tracks:
                ui_tracks.append({
                    "title": t.get("title", "Unknown"),
                    "artist": t.get("artist", "Unknown"),
                    "genre": "Backlink Mix",
                    "plays": 0 # Placeholder until metrics are linked
                })
            
            # Read existing HTML
            with open(html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace the JS data array
            # Finding the start of the array
            start_marker = "const songs = ["
            end_marker = "];"
            
            start_idx = content.find(start_marker)
            if start_idx == -1:
                return
                
            # Find the end of the array block (heuristic)
            end_idx = content.find(end_marker, start_idx)
            if end_idx == -1:
                return
                
            new_json = json.dumps(ui_tracks, indent=4)
            
            # Reconstruct content
            new_content = (
                content[:start_idx + len(start_marker)] + 
                "\n" + new_json[1:-1] + # automated trimming of brackets to fit "const songs = [" ... "];"
                content[end_idx:]
            )
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
                
            self.log("Updated public/songs.html with latest library.")
            
        except Exception as e:
            self.log(f"Failed to update public site: {e}", level="error")

if __name__ == "__main__":
    bee = ConsultantBee()
    bee.work()
