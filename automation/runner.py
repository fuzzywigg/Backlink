import json
import time
import os
from datetime import datetime

class AutonomousRunner:
    def __init__(self, manifest_path="automation/manifest.json"):
        self.manifest_path = manifest_path
        self.stop_signal_file = "automation/STOP.signal"
        self.log_file = "automation/session.log"
        self._load_manifest()

    def _load_manifest(self):
        with open(self.manifest_path, 'r') as f:
            self.manifest = json.load(f)

    def _save_manifest(self):
        with open(self.manifest_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)

    def log(self, message):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {message}"
        print(entry)
        with open(self.log_file, 'a') as f:
            f.write(entry + "\n")

    def check_stop_hook(self):
        if os.path.exists(self.stop_signal_file):
            self.log("🛑 STOP SIGNAL DETECTED. Halting operations.")
            return True
        return False

    def execute_next(self):
        for task in self.manifest:
            if task['status'] == 'pending':
                task_id = task['id']
                self.log(f"Starting Task: {task_id} - {task['description']}")
                
                # Check Stop Hook BEFORE starting
                if self.check_stop_hook():
                    return False

                try:
                    # In a real autonomy loop, this would trigger the actual Agent Logic.
                    # For this harness, we are marking it 'in_progress' so the Agent knows what to pick up.
                    task['status'] = 'in_progress'
                    self._save_manifest()
                    
                    self.log(f"Task {task_id} marked as IN_PROGRESS. Waiting for Agent execution...")
                    return True # We only enact one state change per 'tick' to allow the LLM to do the work.
                    
                except Exception as e:
                    self.log(f"❌ Error in Task {task_id}: {str(e)}")
                    task['status'] = 'failed'
                    self._save_manifest()
                    return False
        
        self.log("✅ All tasks in manifest completed!")
        return False

if __name__ == "__main__":
    runner = AutonomousRunner()
    runner.execute_next()
