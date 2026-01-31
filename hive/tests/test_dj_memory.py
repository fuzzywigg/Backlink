"""
Tests for DJ Memory Manager.
"""

import json
import shutil
import tempfile
from pathlib import Path

import pytest

from hive.utils.dj_memory import DJMemory


@pytest.fixture
def temp_hive_path():
    """Create a temporary hive directory for testing."""
    temp_dir = tempfile.mkdtemp()
    hive_path = Path(temp_dir) / "hive"
    hive_path.mkdir(parents=True)
    (hive_path / "honeycomb").mkdir(parents=True)

    yield hive_path

    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def dj_memory(temp_hive_path):
    """Create a DJMemory instance for testing."""
    return DJMemory(hive_path=temp_hive_path)


class TestSongHistory:
    """Test song history tracking."""

    def test_track_song_played(self, dj_memory):
        """Test tracking a played song."""
        dj_memory.track_song_played(
            song_title="Test Song",
            artist="Test Artist",
            genre="Rock",
            mood="Energetic"
        )

        recent = dj_memory.get_recent_songs(limit=1)
        assert len(recent) == 1
        assert recent[0]["title"] == "Test Song"
        assert recent[0]["artist"] == "Test Artist"
        assert recent[0]["genre"] == "Rock"

    def test_get_recent_songs(self, dj_memory):
        """Test retrieving recent songs."""
        # Add multiple songs
        for i in range(5):
            dj_memory.track_song_played(
                song_title=f"Song {i}",
                artist=f"Artist {i}"
            )

        recent = dj_memory.get_recent_songs(limit=3)
        assert len(recent) == 3
        # Most recent should be first
        assert recent[0]["title"] == "Song 4"

    def test_was_song_played_recently(self, dj_memory):
        """Test checking if song was played recently."""
        dj_memory.track_song_played(
            song_title="Recent Song",
            artist="Recent Artist"
        )

        # Should be found
        assert dj_memory.was_song_played_recently(
            "Recent Song",
            "Recent Artist",
            hours=1
        )

        # Should not be found (different song)
        assert not dj_memory.was_song_played_recently(
            "Other Song",
            "Other Artist",
            hours=1
        )

    def test_genre_distribution(self, dj_memory):
        """Test genre distribution calculation."""
        # Add songs with different genres
        dj_memory.track_song_played("Song 1", "Artist 1", genre="Rock")
        dj_memory.track_song_played("Song 2", "Artist 2", genre="Rock")
        dj_memory.track_song_played("Song 3", "Artist 3", genre="Jazz")

        distribution = dj_memory.get_genre_distribution(hours=1)

        assert distribution["Rock"] == 2
        assert distribution["Jazz"] == 1

    def test_song_history_limit(self, dj_memory):
        """Test that song history is limited to 100 entries."""
        # Add 150 songs
        for i in range(150):
            dj_memory.track_song_played(f"Song {i}", f"Artist {i}")

        recent = dj_memory.get_recent_songs(limit=200)
        # Should only keep 100
        assert len(recent) == 100


class TestListenerProfiles:
    """Test listener profile management."""

    def test_remember_listener(self, dj_memory):
        """Test storing listener profile."""
        dj_memory.remember_listener(
            listener_id="listener_123",
            name="John Doe",
            location="Seattle, WA"
        )

        profile = dj_memory.get_listener_profile("listener_123")
        assert profile is not None
        assert profile["name"] == "John Doe"
        assert profile["location"] == "Seattle, WA"
        assert profile["interactions"] == 1

    def test_update_listener(self, dj_memory):
        """Test updating existing listener."""
        # Initial save
        dj_memory.remember_listener(
            listener_id="listener_456",
            name="Jane"
        )

        # Update with new info
        dj_memory.remember_listener(
            listener_id="listener_456",
            location="Portland"
        )

        profile = dj_memory.get_listener_profile("listener_456")
        assert profile["name"] == "Jane"
        assert profile["location"] == "Portland"
        assert profile["interactions"] == 2

    def test_get_all_listeners(self, dj_memory):
        """Test retrieving all listeners."""
        # Add multiple listeners
        for i in range(5):
            dj_memory.remember_listener(f"listener_{i}", name=f"User {i}")

        all_listeners = dj_memory.get_all_listeners()
        assert len(all_listeners) == 5

    def test_listener_sorting(self, dj_memory):
        """Test listeners are sorted by interactions."""
        dj_memory.remember_listener("listener_a", name="User A")
        dj_memory.remember_listener("listener_b", name="User B")

        # Add more interactions to listener_b
        dj_memory.remember_listener("listener_b", name="User B")
        dj_memory.remember_listener("listener_b", name="User B")

        all_listeners = dj_memory.get_all_listeners()
        # listener_b should be first (more interactions)
        assert all_listeners[0]["id"] == "listener_b"


class TestAntiRepetition:
    """Test anti-repetition tracking."""

    def test_track_phrase_usage(self, dj_memory):
        """Test tracking phrase usage."""
        dj_memory.track_phrase_usage(
            "Redrawing the map",
            category="transition"
        )

        assert dj_memory.was_phrase_used_recently(
            "Redrawing the map",
            hours=1
        )

    def test_phrase_case_insensitive(self, dj_memory):
        """Test phrase tracking is case-insensitive."""
        dj_memory.track_phrase_usage("Technical Meridian")

        # Should match regardless of case
        assert dj_memory.was_phrase_used_recently("technical meridian")
        assert dj_memory.was_phrase_used_recently("TECHNICAL MERIDIAN")

    def test_phrase_usage_count(self, dj_memory):
        """Test counting phrase usage."""
        phrase = "structural signal"

        # Track multiple times
        for _ in range(3):
            dj_memory.track_phrase_usage(phrase)

        count = dj_memory.get_phrase_usage_count(phrase, hours=1)
        assert count == 3

    def test_phrase_usage_time_window(self, dj_memory):
        """Test phrase usage respects time window."""
        dj_memory.track_phrase_usage("test phrase")

        # Should be found in 1-hour window
        assert dj_memory.was_phrase_used_recently("test phrase", hours=1)

        # Should still be found in 24-hour window
        assert dj_memory.was_phrase_used_recently("test phrase", hours=24)


class TestSessionContext:
    """Test session context management."""

    def test_set_session_context(self, dj_memory):
        """Test setting session context."""
        dj_memory.set_session_context("current_show", "Morning Show")

        value = dj_memory.get_session_context("current_show")
        assert value == "Morning Show"

    def test_session_context_types(self, dj_memory):
        """Test session context with different types."""
        dj_memory.set_session_context("string_val", "test")
        dj_memory.set_session_context("int_val", 42)
        dj_memory.set_session_context("dict_val", {"key": "value"})

        assert dj_memory.get_session_context("string_val") == "test"
        assert dj_memory.get_session_context("int_val") == 42
        assert dj_memory.get_session_context("dict_val") == {"key": "value"}

    def test_clear_session_context(self, dj_memory):
        """Test clearing session context."""
        dj_memory.set_session_context("key1", "value1")
        dj_memory.set_session_context("key2", "value2")

        dj_memory.clear_session_context()

        assert dj_memory.get_session_context("key1") is None
        assert dj_memory.get_session_context("key2") is None


class TestMemoryPersistence:
    """Test memory persistence across instances."""

    def test_memory_persists(self, temp_hive_path):
        """Test that memory persists to disk."""
        # Create first instance and add data
        memory1 = DJMemory(hive_path=temp_hive_path)
        memory1.track_song_played("Test Song", "Test Artist")
        memory1.remember_listener("listener_1", name="Test User")

        # Create second instance (should load from disk)
        memory2 = DJMemory(hive_path=temp_hive_path)

        # Verify data was loaded
        songs = memory2.get_recent_songs()
        assert len(songs) == 1
        assert songs[0]["title"] == "Test Song"

        profile = memory2.get_listener_profile("listener_1")
        assert profile is not None
        assert profile["name"] == "Test User"

    def test_memory_file_created(self, temp_hive_path):
        """Test that memory file is created."""
        memory = DJMemory(hive_path=temp_hive_path)
        memory.track_song_played("Song", "Artist")

        memory_file = temp_hive_path / "honeycomb" / "dj_memory.json"
        assert memory_file.exists()

        # Verify it's valid JSON
        with open(memory_file) as f:
            data = json.load(f)

        assert "song_history" in data
        assert "listeners" in data


class TestMemoryUtilities:
    """Test utility methods."""

    def test_get_memory_summary(self, dj_memory):
        """Test memory summary."""
        dj_memory.track_song_played("Song", "Artist")
        dj_memory.remember_listener("listener_1", name="User")
        dj_memory.track_phrase_usage("phrase")

        summary = dj_memory.get_memory_summary()

        assert summary["total_songs_tracked"] == 1
        assert summary["known_listeners"] == 1
        assert summary["phrases_tracked"] == 1

    def test_reset_memory(self, dj_memory):
        """Test resetting memory."""
        # Add some data
        dj_memory.track_song_played("Song", "Artist")
        dj_memory.remember_listener("listener_1", name="User")

        # Reset without confirmation should fail
        result = dj_memory.reset_memory(confirm=False)
        assert result is False

        # Should still have data
        assert len(dj_memory.get_recent_songs()) == 1

        # Reset with confirmation
        result = dj_memory.reset_memory(confirm=True)
        assert result is True

        # Should be empty now
        assert len(dj_memory.get_recent_songs()) == 0
        assert len(dj_memory.get_all_listeners()) == 0
