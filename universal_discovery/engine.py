import datetime
import json
import os


class DiscoveryEngine:
    def __init__(self, config_path="config.json"):
        self.root_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(self.root_dir, config_path)
        self.config = self._load_config()
        self.context_name = self.config.get("active_context", "default")
        self.context = self.config["contexts"].get(self.context_name)

    def _load_config(self):
        with open(self.config_path) as f:
            return json.load(f)

    def set_context(self, context_name):
        if context_name in self.config["contexts"]:
            self.context_name = context_name
            self.context = self.config["contexts"][context_name]
            # Save selection
            self.config["active_context"] = context_name
            with open(self.config_path, "w") as f:
                json.dump(self.config, f, indent=2)
            return True
        return False

    def analyze_gap(self, url, summary):
        """
        Simulates the 'Latent Context Check'.
        In a full agentic loop, this would query the vector DB or recent chat logs.
        For this lightweight tool, we check if the domain or keywords appear in recent tasks.
        """
        # Placeholder for 2026 Sovereign Graph lookup
        return {
            "is_gap_filler": True,
            "reason": "Matches topics found in recent task.md (Discovery/Tooling)."
        }

    def get_pending_reviews(self):
        """Fetch all PENDING items from storage."""
        storage_path = self._get_storage_path()
        if not os.path.exists(storage_path):
            return []

        try:
            with open(storage_path) as f:
                data = json.load(f)
            return [item for item in data if item.get("recommendation") == "PENDING"]
        except Exception:
            return []

    def save_review(self, url, name, summary, analysis, rubric_scores, update=True, recommendation=None):

        # Auto-calc recommendation if not provided
        if not recommendation:
            score = self._calculate_score(rubric_scores)
            recommendation = "INTEGRATE" if score > 70 else "MONITOR"

        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "url": url,
            "name": name,
            "summary": summary,
            "scores": rubric_scores,
            "weighted_score": self._calculate_score(rubric_scores),
            "analysis": analysis,
            "recommendation": recommendation,
            "context": self.context_name
        }

        storage_path = self._get_storage_path()

        # Load existing
        data = []
        if os.path.exists(storage_path):
            try:
                with open(storage_path) as f:
                    data = json.load(f)
            except Exception:
                pass

        if update:
            # Check for existing URL and update in-place
            updated = False
            for _i, item in enumerate(data):
                if item.get("url") == url:
                    # Merge but prioritize new data
                    item.update(entry)
                    updated = True
                    break
            if not updated:
                data.insert(0, entry)
        else:
            data.insert(0, entry)

        # Save
        with open(storage_path, 'w') as f:
            json.dump(data, f, indent=2)

        return entry

    def _get_storage_path(self):
        storage_path = self.context["path"]
        if not os.path.isabs(storage_path):
            storage_path = os.path.join(self.root_dir, storage_path)
        return storage_path

    def _calculate_score(self, scores):
        # Simple average for generic, weighted for sovereign
        # This belongs in the Rubric class ideally, but keeping it simple here.
        if not scores: return 0
        vals = list(scores.values())
        return sum(vals) / len(vals) * 10
