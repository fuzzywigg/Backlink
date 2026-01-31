"""
Show Prep Bee - Prepares content for the broadcast.

Responsibilities:
- Research topics for DJ banter
- Pull relevant news/events for listener locations
- Prepare talking points
- Queue up trivia and fun facts
"""

import os
import json
import logging
from typing import Any
from datetime import datetime

from dotenv import load_dotenv
from google import genai
from google.genai import types

from hive.bees.base_bee import EmployedBee
from hive.utils.trivia_fetcher import TriviaFetcher
from core_utils.ontology_manager import OntologyManager

# Configure Logging
logger = logging.getLogger("ShowPrepBee")

class ShowPrepBee(EmployedBee):
    """
    Prepares show content and talking points.
    
    Now integrated with OntologyManager (v3.2) to prevent linguistic repetition.
    Uses Gemini VS-Flash/Pro to generate fresh banter based on the active 'Vibe'.
    """

    BEE_TYPE = "show_prep"
    BEE_NAME = "Show Prep Bee"
    CATEGORY = "content"

    def __init__(self, hive_path: str | None = None):
        super().__init__(hive_path)
        load_dotenv() # Load environment variables
        self.ontology_manager = OntologyManager()
        
        # Initialize Gemini Client
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        
        if not api_key:
             # Fallback to key file if environment not set
             try:
                 with open("hive/keys.json") as f:
                     data = json.load(f)
                     api_key = data.get("GEMINI_API_KEY") or data.get("GOOGLE_API_KEY")
             except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
                 logger.warning(f"Could not load API key from keys.json: {e}")
        
        self.client = genai.Client(api_key=api_key) if api_key else None
        if not self.client:
            logger.warning("Gemini Client not initialized. Falling back to static text.")

    def work(self, task: dict[str, Any] | None = None) -> dict[str, Any]:
        """
        Generate show prep materials.
        """
        self.log("Starting show prep with Ontology Injection...")

        # Read current intel
        intel = self.read_intel()
        
        # Determine time slot
        time_slot = "evening"
        if task and "time_slot" in task:
            time_slot = task["time_slot"]

        # Get Current Ontology/Vibe
        current_ontology = self.ontology_manager.get_current_ontology()
        self.log(f"Active Ontology: {current_ontology.get('id')} ({current_ontology.get('vibe')})")

        prep_materials = {
            "time_slot": time_slot,
            "ontology": current_ontology,
            "talking_points": [],
            "listener_shoutouts": [],
            "trivia": [],
            "local_context": {},
        }

        # Generate fresh talking points using LLM + Ontology
        prep_materials["talking_points"] = self._generate_llm_banter(time_slot, current_ontology)

        # Pull listener intel for shoutouts
        known_nodes = intel.get("listeners", {}).get("known_nodes", {})
        for node_id, node_data in known_nodes.items():
            if node_data.get("location"):
                shoutout = self._prepare_shoutout(node_id, node_data)
                prep_materials["listener_shoutouts"].append(shoutout)

        # Generate trivia
        prep_materials["trivia"] = self._generate_trivia()

        # Write to state for DJ to pick up
        self.write_state({"show_prep": prep_materials})

        self.log(
            f"Prep complete: {len(prep_materials['talking_points'])} talking points generated."
        )

        return prep_materials

    def _generate_llm_banter(self, time_slot: str, ontology: dict) -> list:
        """
        Generates banter using Gemini, injected with the current Ontology.
        """
        if not self.client:
            return self._get_static_fallback(time_slot)

        prompt = f"""
        Generate 3 short, distinct DJ banter lines for a radio station.
        
        CONTEXT:
        - Time Slot: {time_slot}
        - Current Vibe/Persona: {ontology.get('vibe')}
        - Style Instruction: {ontology.get('prompt_injection')}
        
        CONSTRAINTS:
        - Do NOT use these banned words: {', '.join(ontology.get('banned_words', []))}
        - Keep it under 20 words per line.
        - Be cool, atmospheric, and immersive.
        - STRICTLY prevent repetition of words like "manifest", "blueprint", "organism".
        
        OUTPUT FORMAT:
        JSON list of objects: [{{ "type": "intro|outro|transition", "text": "..." }}]
        """

        try:
            response = self.client.models.generate_content(
                model="gemini-2.0-flash-exp",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            
            # clean potential markdown fences
            text = response.text.replace('```json', '').replace('```', '').strip()
            return json.loads(text)

        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            return self._get_static_fallback(time_slot)

    def _get_static_fallback(self, time_slot: str) -> list:
        """Original static dictionary for fallback."""
        points_by_slot = {
            "morning": [
                {"type": "energy", "text": "Rise and grind. New day, new frequencies."},
                {"type": "weather", "text": "Check your local conditions before heading out."},
                {"type": "motivation", "text": "The queue is locked and loaded. Let's move."},
            ],
            "afternoon": [
                {"type": "focus", "text": "Midday momentum. Stay locked in."},
                {"type": "productivity", "text": "This one's for the grinders still at it."},
                {"type": "transition", "text": "Halfway there. Keep the signal strong."},
            ],
            "evening": [
                {"type": "unwind", "text": "Day's done. Time to decompress."},
                {"type": "vibe", "text": "Evening frequencies settling in."},
                {"type": "chill", "text": "No rush now. Just the music."},
            ],
            "night": [
                {"type": "late", "text": "Night owls, you know who you are."},
                {"type": "deep", "text": "The quiet hours. Best transmission time."},
                {"type": "cosmic", "text": "Out there in the dark, we're all connected."},
            ],
        }
        return points_by_slot.get(time_slot, points_by_slot["evening"])

    def _prepare_shoutout(self, node_id: str, node_data: dict) -> dict:
        """Prepare a personalized shoutout for a listener."""

        location = node_data.get("location", {})
        city = location.get("city", "somewhere out there")

        return {
            "node_id": node_id,
            "city": city,
            "template": f"Signal coming in from {city}. We see you.",
            "context": node_data.get("notes", [])[-1] if node_data.get("notes") else None,
        }

    def _generate_trivia(self) -> list:
        """Generate trivia for commercial break replacements."""

        # Securely read config from hive root, avoiding path traversal
        config = {}
        try:
            with open(self.hive_path / "config.json") as f:
                config = json.load(f)
        except Exception:
            self.log("Warning: Could not load config.json for trivia", level="warning")
            config = {}

        fetcher = TriviaFetcher(config)
        return fetcher.fetch(count=3)


if __name__ == "__main__":
    # Test run
    bee = ShowPrepBee()
    result = bee.run({"time_slot": "evening"})
    print(result)
