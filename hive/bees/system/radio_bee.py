import json
import random
from pathlib import Path

from core_utils.model_registry_loader import ModelRegistryLoader
from core_utils.ontology_manager import OntologyManager
from hive.bees.base_bee import BaseBee
from hive.utils.radio_bridge import radio


class RadioBee(BaseBee):
    """
    The DJ of the Hive. Manages the radio stream, intentions, and resource requests.
    Interfaces with Goose FM via the RadioBridge.
    """

    def __init__(self, name="RadioBee", song_lib_path="song_library/songs"):
        super().__init__(name=name)
        self.song_lib_path = Path(song_lib_path)
        self.current_track = None
        self.intentions = []
        self.ontology = OntologyManager()
        self.models = ModelRegistryLoader()

    def get_voice_settings(self):
        """Retrieves the current hour's ontology and model spec."""
        current_vibe = self.ontology.get_current_ontology()
        # Example: select model based on vibe complexity (placeholder logic)
        model_id = self.models.recommend_model(mode="performance")
        return current_vibe, model_id

    def load_library(self):
        """Loads available songs from the library."""
        songs = []
        if self.song_lib_path.exists():
            for f in self.song_lib_path.glob("*.json"):
                try:
                    with open(f) as song_file:
                        songs.append(json.load(song_file))
                except Exception as e:
                    self.log(f"Error loading song {f}: {e}")
        return songs

    def spin_track(self, intent_filter=None):
        """
        Selects and 'plays' a track.
        In a real scenario, this would trigger the actual audio source.
        """
        songs = self.load_library()
        if not songs:
            self.log("No songs in library!")
            return

        # Simple random selection for now
        # TODO: Implement intent filtering
        track = random.choice(songs)

        self.current_track = track

        # Update Dashboard
        radio.update_now_playing(
            artist=track.get("artist", "Unknown"),
            track=track.get("title", "Unknown"),
            intent=track.get("intent", "General"),
        )

        # Log intention
        self.announce(f"Spinning {track.get('title')} for {track.get('intent')}")

    def announce(self, message):
        """
        Announces something on the radio log.
        Checks for ontology violations (banned words) before broadcasting.
        """
        # Safety Check
        score = 1.0
        if self.ontology:
            score = self.ontology.validate_text(message, history=[])

        if score < 1.0:
            self.log(f"⚠️ [SAFETY BLOCKED] Message contains banned content: '{message}'")
            return

        radio.log_intention(self.name, message)
        self.log(f"ON AIR: {message}")

    def request_resources(self, need_type, amount, description):
        """
        Posts a need to the dashboard.
        """
        self.announce(f"REQUEST: Need {amount} for {need_type} - {description}")
        # TODO: Add logic to persist this need to a 'Unfulfilled Needs' registry

    def run(self):
        """
        Main loop for the Radio Bee.
        """
        self.announce("Radio System Online. Tuning frequencies...")

        # Check Vibe
        vibe, model = self.get_voice_settings()
        self.announce(f"System State: {model} loaded. Vibe: {vibe['id'].upper()}")

        self.spin_track()


if __name__ == "__main__":
    # Test run
    dj = RadioBee()
    dj.run()
