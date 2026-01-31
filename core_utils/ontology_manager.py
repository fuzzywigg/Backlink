import json
import os
from datetime import datetime

LIBRARY_PATH = "config/ontology_library.json"

class OntologyManager:
    """
    Manages the rotation of linguistic ontologies (vocabularies)
    to prevent repetitive 'Mad Libs' loops in agent outputs.
    """

    def __init__(self, library_path: str = LIBRARY_PATH):
        self.library_path = library_path
        self.library = self._load_library()
        self.current_ontology = None

    def _load_library(self) -> dict:
        if not os.path.exists(self.library_path):
            return {}
        try:
            with open(self.library_path) as f:
                return json.load(f)
        except Exception as e:
            print(f"[Ontology] Load error: {e}")
            return {}

    def get_current_ontology(self, offset_hour: int = 0, override_hour: int = None) -> dict:
        """
        Determines the ontology based on the current hour.
        Rotation Cycle:
        00-06: Cyber Noir
        06-12: Solar Punk
        12-18: High Tech
        18-24: Abstract Flow
        """
        if override_hour is not None:
             hour = (override_hour + offset_hour) % 24
        else:
             now = datetime.now()
             hour = (now.hour + offset_hour) % 24


        # Quadrant check
        if 0 <= hour < 6:
            key = "cyber_noir"
        elif 6 <= hour < 12:
            key = "solar_punk"
        elif 12 <= hour < 18:
            key = "high_tech"
        else:
            key = "abstract_flow"

        # Safe fallback if config is broken
        if "ontologies" not in self.library or key not in self.library["ontologies"]:
            return self._get_fallback_ontology()

        self.current_ontology = self.library["ontologies"][key]
        return self.current_ontology

    def _get_fallback_ontology(self):
        return {
            "id": "fallback",
            "vibe": "Neutral",
            "prompt_injection": "Speak clearly and concisely."
        }

    def validate_text(self, text: str, history: list[str]) -> float:
        """
        Scores text for freshness.
        0.0 = Repetitive trash
        1.0 = Fresh and compliant
        """
        if not text:
            return 0.0

        # 1. Check Banned Words
        if self.current_ontology and "banned_words" in self.current_ontology:
            for word in self.current_ontology["banned_words"]:
                if word.lower() in text.lower():
                    print(f"[Ontology] Violation: Banned word '{word}' found.")
                    return 0.5 # Penalty

        # 2. Check Repetition against History
        # (Simple N-gram overlap or keyword check would go here)

        return 1.0

if __name__ == "__main__":
    manager = OntologyManager()
    ontology = manager.get_current_ontology()
    print(f"Current Vibe ({datetime.now().hour}h): {ontology['id']}")
    print(f"Injection: {ontology['prompt_injection']}")
