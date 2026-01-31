"""
DJ Memory Manager - Unified memory interface for AI DJ.

This module provides a high-level interface for the DJ to:
- Track song playback history
- Remember listener information and preferences
- Store conversation context
- Maintain anti-repetition tracking
- Build long-term personality continuity

Designed to work with Agent.md instructions for context-aware broadcasting.
"""

import json
import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from hive.utils.state_manager import StateManager

logger = logging.getLogger(__name__)


class DJMemory:
    """
    Memory manager for AI DJ operations.

    Provides simplified interface for:
    - Song history tracking
    - Listener profiles
    - Phrase repetition monitoring
    - Session context management
    """

    def __init__(self, hive_path: Path | None = None):
        """Initialize DJ Memory.

        Args:
            hive_path: Path to hive directory (optional)
        """
        self.state_manager = StateManager(hive_path)
        self.hive_path = self.state_manager.hive_path
        self.memory_path = self.hive_path / "honeycomb" / "dj_memory.json"
        self._cache: dict[str, Any] = {}
        self._dirty: bool = False  # Track if cache needs saving
        self._load_memory()

    def _load_memory(self) -> None:
        """Load DJ memory from disk."""
        if self.memory_path.exists():
            try:
                with open(self.memory_path) as f:
                    self._cache = json.load(f)
                logger.info(f"Loaded DJ memory from {self.memory_path}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in DJ memory file: {e}")
                self._cache = self._initialize_memory_structure()
            except Exception as e:
                logger.error(f"Could not load DJ memory: {e}")
                self._cache = self._initialize_memory_structure()
        else:
            logger.info(
                f"No existing DJ memory found, initializing new memory at {self.memory_path}"
            )
            self._cache = self._initialize_memory_structure()

    def _initialize_memory_structure(self) -> dict[str, Any]:
        """Initialize empty memory structure."""
        return {
            "song_history": [],  # Recent songs played
            "listeners": {},  # Listener profiles
            "phrases_used": {},  # Anti-repetition tracking
            "session_context": {},  # Current session data
            "preferences": {},  # Station preferences
            "metadata": {"created_at": datetime.now(timezone.utc).isoformat(), "version": "1.0.0"},
        }

    def _save_memory(self, force: bool = False) -> None:
        """Persist memory to disk.

        Args:
            force: Force save even if not dirty
        """
        if not force and not self._dirty:
            return

        try:
            self.memory_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.memory_path, "w") as f:
                json.dump(self._cache, f, indent=2)
            self._dirty = False
            logger.debug(f"Saved DJ memory to {self.memory_path}")
        except OSError as e:
            logger.error(f"Could not create directory for DJ memory: {e}")
        except Exception as e:
            logger.error(f"Could not save DJ memory: {e}")

    # Song History Methods

    def track_song_played(
        self, song_title: str, artist: str, genre: str | None = None, mood: str | None = None
    ) -> None:
        """
        Record a song that was played.

        Args:
            song_title: Title of the song (required, non-empty)
            artist: Artist name (required, non-empty)
            genre: Optional genre classification
            mood: Optional mood descriptor

        Raises:
            ValueError: If song_title or artist is empty
        """
        if not song_title or not song_title.strip():
            raise ValueError("song_title cannot be empty")
        if not artist or not artist.strip():
            raise ValueError("artist cannot be empty")

        timestamp = datetime.now(timezone.utc).isoformat()

        song_entry = {
            "title": song_title.strip(),
            "artist": artist.strip(),
            "genre": genre.strip() if genre else None,
            "mood": mood.strip() if mood else None,
            "played_at": timestamp,
        }

        self._cache["song_history"].insert(0, song_entry)

        # Keep only last 100 songs in memory
        if len(self._cache["song_history"]) > 100:
            self._cache["song_history"] = self._cache["song_history"][:100]
            logger.debug("Trimmed song history to last 100 entries")

        self._dirty = True
        self._save_memory()
        logger.debug(f"Tracked song: '{song_title}' by {artist}")

    def get_recent_songs(self, limit: int = 10) -> list[dict[str, Any]]:
        """
        Get recently played songs.

        Args:
            limit: Number of recent songs to return

        Returns:
            List of song dictionaries
        """
        return self._cache["song_history"][:limit]

    def was_song_played_recently(self, song_title: str, artist: str, hours: int = 4) -> bool:
        """
        Check if a song was played within the specified time window.

        Args:
            song_title: Title to check
            artist: Artist to check
            hours: Time window in hours

        Returns:
            True if song was played recently
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        for song in self._cache["song_history"]:
            played_at = datetime.fromisoformat(song["played_at"])
            if played_at > cutoff and (
                song["title"].lower() == song_title.lower()
                and song["artist"].lower() == artist.lower()
            ):
                return True

        return False

    def get_genre_distribution(self, hours: int = 2) -> dict[str, int]:
        """
        Get genre distribution for recent plays.

        Args:
            hours: Time window to analyze

        Returns:
            Dictionary mapping genre to play count
        """
        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        distribution: dict[str, int] = defaultdict(int)

        for song in self._cache["song_history"]:
            played_at = datetime.fromisoformat(song["played_at"])
            if played_at > cutoff and song.get("genre"):
                distribution[song["genre"]] += 1

        return dict(distribution)

    # Listener Profile Methods

    def remember_listener(
        self,
        listener_id: str,
        name: str | None = None,
        location: str | None = None,
        preferences: dict[str, Any] | None = None,
    ) -> None:
        """
        Store or update listener profile.

        Args:
            listener_id: Unique listener identifier (required, non-empty)
            name: Listener's name
            location: Listener's location
            preferences: Optional preferences dictionary

        Raises:
            ValueError: If listener_id is empty
        """
        if not listener_id or not listener_id.strip():
            raise ValueError("listener_id cannot be empty")

        listener_id = listener_id.strip()

        if listener_id not in self._cache["listeners"]:
            self._cache["listeners"][listener_id] = {
                "id": listener_id,
                "first_seen": datetime.now(timezone.utc).isoformat(),
                "interactions": 0,
            }
            logger.debug(f"Created new listener profile: {listener_id}")

        listener = self._cache["listeners"][listener_id]

        if name:
            listener["name"] = name.strip()
        if location:
            listener["location"] = location.strip()
        if preferences:
            listener["preferences"] = preferences

        listener["last_seen"] = datetime.now(timezone.utc).isoformat()
        listener["interactions"] += 1

        self._dirty = True
        self._save_memory()
        logger.debug(
            f"Updated listener profile: {listener_id} (interactions: {listener['interactions']})"
        )

    def get_listener_profile(self, listener_id: str) -> dict[str, Any] | None:
        """
        Retrieve listener profile.

        Args:
            listener_id: Listener identifier

        Returns:
            Listener profile dictionary or None
        """
        return self._cache["listeners"].get(listener_id)

    def get_all_listeners(self, limit: int | None = None) -> list[dict[str, Any]]:
        """
        Get all known listeners.

        Args:
            limit: Optional limit on number of listeners

        Returns:
            List of listener profiles
        """
        listeners = list(self._cache["listeners"].values())

        # Sort by interaction count and recency
        listeners.sort(
            key=lambda x: (x.get("interactions", 0), x.get("last_seen", "")), reverse=True
        )

        if limit:
            return listeners[:limit]
        return listeners

    # Anti-Repetition Tracking

    def track_phrase_usage(self, phrase: str, category: str = "general") -> None:
        """
        Track usage of a phrase for anti-repetition.

        Args:
            phrase: The phrase that was used
            category: Category of phrase (e.g., "transition", "greeting")
        """
        timestamp = datetime.now(timezone.utc).isoformat()

        phrase_key = phrase.lower().strip()

        if phrase_key not in self._cache["phrases_used"]:
            self._cache["phrases_used"][phrase_key] = []

        self._cache["phrases_used"][phrase_key].append(
            {"timestamp": timestamp, "category": category}
        )

        # Keep only last 20 uses per phrase
        if len(self._cache["phrases_used"][phrase_key]) > 20:
            self._cache["phrases_used"][phrase_key] = self._cache["phrases_used"][phrase_key][-20:]

        self._dirty = True
        self._save_memory()

    def was_phrase_used_recently(self, phrase: str, hours: int = 1) -> bool:
        """
        Check if a phrase was used recently.

        Args:
            phrase: Phrase to check
            hours: Time window in hours

        Returns:
            True if phrase was used recently
        """
        phrase_key = phrase.lower().strip()

        if phrase_key not in self._cache["phrases_used"]:
            return False

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

        for usage in self._cache["phrases_used"][phrase_key]:
            used_at = datetime.fromisoformat(usage["timestamp"])
            if used_at > cutoff:
                return True

        return False

    def get_phrase_usage_count(self, phrase: str, hours: int | None = None) -> int:
        """
        Get how many times a phrase was used.

        Args:
            phrase: Phrase to check
            hours: Optional time window in hours

        Returns:
            Usage count
        """
        phrase_key = phrase.lower().strip()

        if phrase_key not in self._cache["phrases_used"]:
            return 0

        if hours is None:
            return len(self._cache["phrases_used"][phrase_key])

        cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
        count = 0

        for usage in self._cache["phrases_used"][phrase_key]:
            used_at = datetime.fromisoformat(usage["timestamp"])
            if used_at > cutoff:
                count += 1

        return count

    # Session Context Methods

    def set_session_context(self, key: str, value: Any) -> None:
        """
        Store session-level context data.

        Args:
            key: Context key
            value: Context value (must be JSON-serializable)
        """
        self._cache["session_context"][key] = {
            "value": value,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        self._dirty = True
        self._save_memory()

    def get_session_context(self, key: str) -> Any | None:
        """
        Retrieve session context.

        Args:
            key: Context key

        Returns:
            Context value or None
        """
        context = self._cache["session_context"].get(key)
        if context:
            return context.get("value")
        return None

    def clear_session_context(self) -> None:
        """Clear all session context."""
        self._cache["session_context"] = {}
        self._dirty = True
        self._save_memory()

    # Utility Methods

    def get_memory_summary(self) -> dict[str, Any]:
        """
        Get summary statistics of DJ memory.

        Returns:
            Dictionary with memory statistics
        """
        return {
            "total_songs_tracked": len(self._cache["song_history"]),
            "known_listeners": len(self._cache["listeners"]),
            "phrases_tracked": len(self._cache["phrases_used"]),
            "session_context_items": len(self._cache["session_context"]),
            "memory_size_kb": self.memory_path.stat().st_size / 1024
            if self.memory_path.exists()
            else 0,
        }

    def reset_memory(self, confirm: bool = False) -> bool:
        """
        Reset all DJ memory (use with caution).

        Args:
            confirm: Must be True to actually reset

        Returns:
            True if reset was performed
        """
        if not confirm:
            return False

        self._cache = self._initialize_memory_structure()
        self._dirty = True
        self._save_memory(force=True)
        logger.info("DJ memory was reset")
        return True
