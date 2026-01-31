import json
import logging
import random
from pathlib import Path
from typing import Any, List
from datetime import datetime, timezone

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
    3. 'Import' these tracks into the Hive Memory (intel.json) as candidates.
    """

    BEE_TYPE = "consultant"
    BEE_NAME = "Consultant Bee"
    CATEGORY = "research"

    def __init__(self, hive_path: str | None = None):
        super().__init__(hive_path)
        self.ontology_manager = OntologyManager()
        # self.llm_client is initialized in BaseBee

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
        # Try finding it relative to hive_path or current dir
        path = self.hive_path / "grok_playlist.json"
        
        if not path.exists():
            # Fallback to current working dir
            path = Path("grok_playlist.json").resolve()
            
        if not path.exists():
            self.log("grok_playlist.json not found.", level="warning")
            return []
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("liked_songs", [])
        except Exception as e:
            self.log(f"Failed to read Grok library: {e}", level="error")
            return []

    def _consult_llm(self, library: List[dict], ontology: dict, trends: List[dict], limit: int) -> List[dict]:
        """
        Asks Gemini to act as a Music Curator picking candidates.
        """
        if not self.llm_client:
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
        JSON list of track objects (keys: title, artist, reason).
        Example: [{{"title": "Song", "artist": "Band", "reason": "Fits vibe"}}]
        """
        
        try:
            # Use generate_content with implicit schema via prompt or backend support
            response = self.llm_client.generate_content(
                prompt=prompt,
                response_schema={"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"title": {"type": "STRING"}, "artist": {"type": "STRING"}, "reason": {"type": "STRING"}}}},
                thinking_level="low"
            )
            
            # Handle potential direct list return from Gemini3Client helper
            if isinstance(response, list):
                return response
            
            # Handle formatted dict
            if isinstance(response, dict):
                if "text" in response:
                    text = response["text"].replace('```json', '').replace('```', '').strip()
                    try:
                        return json.loads(text)
                    except (json.JSONDecodeError, ValueError) as e:
                        self.log(f"Failed to parse JSON from response: {e}", level="warning")
                
                # If Gemini3Client returned other dict structure (e.g. error)
                if "error" in response:
                    self.log(f"LLM Error: {response['error']}", level="error")

            return random.sample(library, min(limit, len(library))) if library else []
            
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
            
        # Use BaseBee's update_intel
        self.update_intel({"music_library": intel["music_library"]})

    def _sync_to_hive_memory(self, tracks: List[dict]):
        """
        Updates intel.json 'music_library.owned' directly (legacy/manual sync).
        """
        intel = self.read_intel()
        
        # Ensure structure exists
        if "music_library" not in intel:
            intel["music_library"] = {"owned": [], "rented": []}
        
        if "owned" not in intel["music_library"]:
            intel["music_library"]["owned"] = []

        current_titles = {t["title"].lower() for t in intel["music_library"]["owned"]}
        
        added_count = 0
        for track in tracks:
            if track["title"].lower() not in current_titles:
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
            self.update_intel({"music_library": intel["music_library"]})
            self._update_public_site(intel["music_library"]["owned"])

    def _update_public_site(self, tracks: List[dict]):
        """
        Regenerates public/songs.html with the latest inventory.
        """
        try:
            html_path = self.hive_path / "public" / "songs.html"
            
            if not html_path.exists():
                return
                
            # Convert Hive tracks to UI format
            ui_tracks = []
            for t in tracks:
                ui_tracks.append({
                    "title": t.get("title", "Unknown"),
                    "artist": t.get("artist", "Unknown"),
                    "genre": "Backlink Mix",
                    "plays": 0 
                })
            
            content = html_path.read_text(encoding='utf-8')
            
            # Robust replacement? Still heuristic based on markers
            start_marker = "const songs = ["
            end_marker = "];"
            
            start_idx = content.find(start_marker)
            if start_idx == -1:
                return
                
            # Find the end of the array block
            # We look for the next "];" after start
            end_idx = content.find(end_marker, start_idx)
            if end_idx == -1:
                return
                
            new_json = json.dumps(ui_tracks, indent=4)
            
            new_content = (
                content[:start_idx + len(start_marker)] + 
                "\n" + new_json[1:-1] + # trimmed brackets
                content[end_idx:]
            )
            
            html_path.write_text(new_content, encoding='utf-8')
            self.log("Updated public/songs.html with latest library.")
            
        except Exception as e:
            self.log(f"Failed to update public site: {e}", level="error")

if __name__ == "__main__":
    bee = ConsultantBee()
    bee.run()
