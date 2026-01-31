import datetime
import json
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

    def submit_intention(self, bee_name, message, category="GENERAL"):
        """
        Submits an intention to the queue for the DJ to review/broadcast.
        """
        status = self._read_status()
        if 'intention_queue' not in status:
            status['intention_queue'] = []

        intention = {
            'id': f"{bee_name}-{int(datetime.datetime.now().timestamp())}",
            'bee': bee_name,
            'message': message,
            'category': category,
            'status': 'PENDING', # PENDING, BROADCAST, REJECTED
            'timestamp': datetime.datetime.now().isoformat()
        }

        status['intention_queue'].append(intention)
        self._write_status(status)
        print(f"[{datetime.datetime.now()}] RadioBridge: Intention submitted by {bee_name}")

    def log_intention(self, bee_name, message, status_tag="BROADCAST"):
        """
        Logs a specific (usually broadcasted) intention to the public feed.
        """
        status = self._read_status()
        if 'intentions' not in status:
            status['intentions'] = []

        status['intentions'].insert(0, {
            'bee': bee_name,
            'message': message,
            'status': status_tag,
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

    def submit_need(self, bee_name, need_type, amount, description):
        """
        Submits a resource need (money, compute, fix) to the dashboard.
        """
        status = self._read_status()
        if 'needs_queue' not in status:
            status['needs_queue'] = []

        need_id = f"need-{int(datetime.datetime.now().timestamp())}-{random.randint(100,999)}"

        need = {
            'id': need_id,
            'bee': bee_name,
            'type': need_type, # MONEY, COMPUTE, FIX
            'amount': amount,
            'description': description,
            'status': 'OPEN',
            'timestamp': datetime.datetime.now().isoformat()
        }

        status['needs_queue'].append(need)
        self._write_status(status)
        print(f"[{datetime.datetime.now()}] RadioBridge: Need submitted: {description} (${amount})")
        return need_id

    def resolve_need(self, need_id):
        """
        Marks a need as fulfilled/funded.
        """
        status = self._read_status()
        if 'needs_queue' in status:
            for need in status['needs_queue']:
                if need['id'] == need_id:
                    need['status'] = 'FULFILLED'
                    need['fulfilled_at'] = datetime.datetime.now().isoformat()
                    self._write_status(status)
                    print(f"[{datetime.datetime.now()}] RadioBridge: Need {need_id} fulfilled!")
                    return True
        return False

    def _read_status(self):
        if self.storage_path.exists():
            try:
                with open(self.storage_path) as f:
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
