import json
import os
import datetime
from pathlib import Path

# Placeholder for Goose FM MCP Client
# In the future, this would import the MCP client to talk to the stdio server

class RadioBridge:
    def __init__(self, storage_path="frontend/radio/status.json"):
        """
        Bridge to communicate between Hive Bees and the Radio Dashboard.
        Assuming dashboard reads from a shared JSON file or eventually an API.
        """
        self.storage_path = Path(storage_path)
        # Ensure directory exists if we are writing directly to frontend (dev mode)
        # In prod, this might write to a DB or bucket
        
    def update_now_playing(self, artist, track, intent=None):
        """
        Updates the 'Now Playing' status.
        """
        status = self._read_status()
        status['now_playing'] = {
            'artist': artist,
            'track': track,
            'intent': intent,
            'timestamp': datetime.datetime.now().isoformat()
        }
        self._write_status(status)
        print(f"[{datetime.datetime.now()}] RadioBridge: Now playing {artist} - {track}")

    def log_intention(self, bee_name, message):
        """
        Logs a bee's intention to the radio feed.
        """
        status = self._read_status()
        if 'intentions' not in status:
            status['intentions'] = []
        
        status['intentions'].insert(0, {
            'bee': bee_name,
            'message': message,
            'timestamp': datetime.datetime.now().isoformat()
        })
        # Keep log short
        status['intentions'] = status['intentions'][:50]
        self._write_status(status)

    def tune_frequency(self, frequency):
        """
        Command to tune the physical radio via Goose FM.
        """
        # TODO: Implement actual MCP call to Goose FM
        print(f"RADIO_BRIDGE: Tuning hardware to {frequency} MHz via Goose FM...")
        self.log_intention("RADIO_BEE", f"Tuning SDR to {frequency} MHz")
        return True

    def _read_status(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _write_status(self, data):
        # Depending on deployment, we might not be able to write local files in Cloud Run
        # This is a placeholder logic for the "Proto" phase
        try:
             # Ensure parent dir exists
            if not self.storage_path.parent.exists():
                 return # Fail silently if path is invalid in this context
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"RadioBridge Error: Could not write status: {e}")

# Singleton instance
radio = RadioBridge()
