import requests
import json
import time
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Initial sovereign fallback for bootstrapping (if API fails)
FALLBACK_REGISTRY = {
    "openai": {
        "models": {
            "gpt-4o": {
                "id": "gpt-4o",
                "name": "GPT-4o",
                "context": 128000,
                "cost": {"input": 5.0, "output": 15.0},
                "capabilities": ["reasoning", "vision", "tool_call"]
            }
        }
    },
    "anthropic": {
        "models": {
            "claude-3-5-sonnet-latest": {
                "id": "claude-3-5-sonnet-latest",
                "name": "Claude 3.5 Sonnet",
                "context": 200000,
                "cost": {"input": 3.0, "output": 15.0},
                "capabilities": ["reasoning", "vision", "tool_call"]
            }
        }
    },
    "google": {
        "models": {
            "gemini-1.5-pro": {
                "id": "gemini-1.5-pro",
                "name": "Gemini 1.5 Pro",
                "context": 2000000,
                "cost": {"input": 3.5, "output": 10.5},
                "capabilities": ["reasoning", "vision", "audio", "video", "tool_call"]
            }
        }
    }
}

CACHE_FILE = "models_cache.json"
CACHE_DURATION_HOURS = 24
MODELS_DEV_URL = "https://models.dev/api.json"

class ModelRegistryLoader:
    """
    Sovereign Loader for models.dev API.
    Acts as the 'Dynamic Router' source of truth for the Hive.
    """

    def __init__(self, cache_path: str = CACHE_FILE):
        self.cache_path = cache_path
        self.registry = self._load_registry()

    def _load_registry(self) -> Dict[str, Any]:
        """Loads registry from cache or fetches fresh."""
        if self._is_cache_valid():
            try:
                with open(self.cache_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[ModelRegistry] Cache error: {e}. Fetching fresh.")
        
        return self._fetch_fresh_registry()

    def _is_cache_valid(self) -> bool:
        """Checks if cache exists and is fresh."""
        if not os.path.exists(self.cache_path):
            return False
        
        mod_time = datetime.fromtimestamp(os.path.getmtime(self.cache_path))
        if datetime.now() - mod_time > timedelta(hours=CACHE_DURATION_HOURS):
            return False
            
        return True

    def _fetch_fresh_registry(self) -> Dict[str, Any]:
        """Fetches from models.dev and updates cache."""
        try:
            print(f"[ModelRegistry] Fetching fresh specs from {MODELS_DEV_URL}...")
            response = requests.get(MODELS_DEV_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # Save to cache
            with open(self.cache_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            return data
        except Exception as e:
            print(f"[ModelRegistry] Fetch failed: {e}. Using sovereign fallback.")
            return FALLBACK_REGISTRY

    def get_model(self, model_id: str) -> Optional[Dict]:
        """Retrieves specs for a specific model ID."""
        for provider in self.registry.values():
            if "models" in provider:
                if model_id in provider["models"]:
                    return provider["models"][model_id]
        return None

    def recommend_model(self, 
                       mode: str = "performance", 
                       capabilities: List[str] = None) -> str:
        """
        Recommends a model ID based on mode and capabilities.
        Modes: 'performance', 'cost', 'speed'
        """
        # Placeholder logic - this will evolve to use the real 'cost' fields from models.dev
        # For now, it maps intent to our known best-in-class
        
        if mode == "performance":
            return "claude-3-5-sonnet-latest"
        elif mode == "context":
            return "gemini-1.5-pro"
        elif mode == "cost":
            return "gpt-4o-mini" # Assuming it exists in registry
        
        return "gpt-4o"

if __name__ == "__main__":
    # Test run
    loader = ModelRegistryLoader()
    print("Registry Loaded Keys:", loader.registry.keys())
    print("Recommendation (Performance):", loader.recommend_model(mode="performance"))
