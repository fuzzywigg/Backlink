"""
DJ Broadcast Helper - Integration of Agent.md personality with DJ operations.

This module provides helper functions to integrate the Agent.md personality
and DJ memory into broadcast operations, making it easy for the DJ to:
- Load personality context for broadcasts
- Check anti-repetition rules
- Access listener and song history
- Generate context-aware responses
"""

from typing import Any, Optional
from datetime import datetime
from pathlib import Path

from hive.utils.agent_personality import AgentPersonality
from hive.utils.dj_memory import DJMemory


class DJBroadcastHelper:
    """
    Helper class for DJ broadcasts with personality and memory integration.
    
    Combines Agent.md personality with DJ memory for context-aware broadcasting.
    """
    
    def __init__(
        self,
        hive_path: Path | None = None,
        agent_md_path: Path | str | None = None
    ):
        """
        Initialize DJ broadcast helper.
        
        Args:
            hive_path: Path to hive directory
            agent_md_path: Path to Agent.md file
        """
        self.personality = AgentPersonality(agent_md_path)
        self.memory = DJMemory(hive_path)
        self.current_session: dict[str, Any] = {}
    
    def start_session(
        self,
        time_of_day: str | None = None,
        location: str | None = None
    ) -> str:
        """
        Start a new broadcast session.
        
        Args:
            time_of_day: Time period (morning/afternoon/evening)
            location: Primary listener location
            
        Returns:
            Session context string for LLM injection
        """
        # Determine time of day if not provided
        if time_of_day is None:
            time_of_day = self._determine_time_of_day()
        
        # Store session info
        self.current_session = {
            "time_of_day": time_of_day,
            "location": location,
            "started_at": datetime.now().isoformat()
        }
        
        self.memory.set_session_context("current_session", self.current_session)
        
        # Generate broadcast context
        context = self._generate_session_context(time_of_day)
        
        return context
    
    def _determine_time_of_day(self) -> str:
        """Determine time of day from current hour."""
        hour = datetime.now().hour
        
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 18:
            return "afternoon"
        else:
            return "evening"
    
    def _generate_session_context(self, time_of_day: str) -> str:
        """Generate context for broadcast session."""
        # Get personality context
        personality_context = self.personality.get_context_for_broadcast(
            time_of_day=time_of_day,
            include_music_logic=True,
            include_interactions=True
        )
        
        # Add memory context
        recent_songs = self.memory.get_recent_songs(limit=10)
        recent_listeners = self.memory.get_all_listeners(limit=5)
        
        memory_context = [
            "\n## CURRENT SESSION MEMORY",
            "",
            "### Recently Played Songs (Avoid Repeats):",
        ]
        
        if recent_songs:
            for i, song in enumerate(recent_songs, 1):
                memory_context.append(
                    f"{i}. \"{song['title']}\" by {song['artist']} "
                    f"({song.get('genre', 'Unknown')})"
                )
        else:
            memory_context.append("- No recent songs")
        
        memory_context.append("")
        memory_context.append("### Active Listeners:")
        
        if recent_listeners:
            for listener in recent_listeners:
                location = listener.get('location', 'Unknown location')
                name = listener.get('name', listener['id'])
                memory_context.append(
                    f"- {name} from {location} "
                    f"({listener['interactions']} interactions)"
                )
        else:
            memory_context.append("- No recent listeners")
        
        # Combine contexts
        full_context = "\n".join([
            personality_context,
            "",
            "\n".join(memory_context)
        ])
        
        return full_context
    
    def track_song_played(
        self,
        song_title: str,
        artist: str,
        genre: str | None = None,
        mood: str | None = None
    ) -> None:
        """
        Track a song that was played.
        
        Args:
            song_title: Song title
            artist: Artist name
            genre: Optional genre
            mood: Optional mood
        """
        self.memory.track_song_played(song_title, artist, genre, mood)
    
    def can_play_song(
        self,
        song_title: str,
        artist: str,
        hours_since_last_play: int = 4
    ) -> tuple[bool, str]:
        """
        Check if a song can be played (hasn't been played recently).
        
        Args:
            song_title: Song title to check
            artist: Artist name
            hours_since_last_play: Minimum hours since last play
            
        Returns:
            Tuple of (can_play: bool, reason: str)
        """
        was_recent = self.memory.was_song_played_recently(
            song_title,
            artist,
            hours=hours_since_last_play
        )
        
        if was_recent:
            return False, f"Song played within last {hours_since_last_play} hours"
        
        return True, "OK to play"
    
    def check_genre_variety(self, proposed_genre: str, limit: int = 3) -> tuple[bool, str]:
        """
        Check if playing this genre would violate the Rule of 3.
        
        Args:
            proposed_genre: Genre being considered
            limit: Maximum consecutive same-genre plays (default: 3)
            
        Returns:
            Tuple of (is_ok: bool, reason: str)
        """
        recent_songs = self.memory.get_recent_songs(limit=limit)
        
        if len(recent_songs) < limit:
            return True, "Not enough history to check"
        
        # Check if all recent songs are the same genre
        recent_genres = [
            song.get('genre', '').lower() 
            for song in recent_songs[:limit-1]  # Check last N-1 songs
        ]
        
        if all(g == proposed_genre.lower() for g in recent_genres if g):
            return False, f"Would be {limit} consecutive {proposed_genre} tracks (Rule of 3 violation)"
        
        return True, "Genre variety OK"
    
    def remember_listener(
        self,
        listener_id: str,
        name: str | None = None,
        location: str | None = None,
        preferences: dict[str, Any] | None = None
    ) -> None:
        """
        Remember listener information.
        
        Args:
            listener_id: Unique listener ID
            name: Listener name
            location: Listener location
            preferences: Optional preferences dict
        """
        self.memory.remember_listener(listener_id, name, location, preferences)
    
    def get_listener_context(self, listener_id: str) -> str | None:
        """
        Get contextual information about a listener for personalized shoutouts.
        
        Args:
            listener_id: Listener ID
            
        Returns:
            Context string or None if listener unknown
        """
        profile = self.memory.get_listener_profile(listener_id)
        
        if not profile:
            return None
        
        context_parts = []
        
        if profile.get('name'):
            context_parts.append(f"Name: {profile['name']}")
        
        if profile.get('location'):
            context_parts.append(f"Location: {profile['location']}")
        
        if profile.get('interactions'):
            visits = "visits" if profile['interactions'] > 1 else "visit"
            context_parts.append(f"This is their {profile['interactions']}{self._ordinal(profile['interactions'])} {visits}")
        
        return " | ".join(context_parts) if context_parts else None
    
    @staticmethod
    def _ordinal(n: int) -> str:
        """Convert number to ordinal suffix."""
        if 10 <= n % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(n % 10, 'th')
        return suffix
    
    def check_phrase_repetition(self, phrase: str, hours: int = 1) -> tuple[bool, int]:
        """
        Check if a phrase was used recently (anti-repetition).
        
        Args:
            phrase: Phrase to check
            hours: Time window in hours
            
        Returns:
            Tuple of (was_used_recently: bool, usage_count: int)
        """
        was_recent = self.memory.was_phrase_used_recently(phrase, hours)
        count = self.memory.get_phrase_usage_count(phrase, hours)
        
        return was_recent, count
    
    def track_phrase_used(self, phrase: str, category: str = "general") -> None:
        """
        Track that a phrase was used.
        
        Args:
            phrase: Phrase that was used
            category: Category (transition, greeting, etc.)
        """
        self.memory.track_phrase_usage(phrase, category)
    
    def get_forbidden_phrases(self) -> list[str]:
        """
        Get list of forbidden phrases from Agent.md.
        
        Returns:
            List of phrases to avoid
        """
        return self.personality.get_forbidden_phrases()
    
    def validate_content(self, content: str) -> tuple[bool, list[str]]:
        """
        Validate content against anti-repetition rules.
        
        Args:
            content: Content to validate
            
        Returns:
            Tuple of (is_valid: bool, violations: list[str])
        """
        violations = []
        content_lower = content.lower()
        
        # Check forbidden phrases
        for phrase in self.get_forbidden_phrases():
            if phrase.lower() in content_lower:
                was_recent, count = self.check_phrase_repetition(phrase, hours=1)
                if was_recent:
                    violations.append(
                        f"Forbidden phrase '{phrase}' used {count} time(s) in last hour"
                    )
        
        return len(violations) == 0, violations
    
    def get_broadcast_summary(self) -> dict[str, Any]:
        """
        Get summary of current broadcast session.
        
        Returns:
            Dictionary with session statistics
        """
        memory_summary = self.memory.get_memory_summary()
        
        return {
            "session": self.current_session,
            "personality_version": self.personality.version,
            "personality_loaded": self.personality.loaded,
            "memory_stats": memory_summary,
            "recent_songs": len(self.memory.get_recent_songs()),
            "known_listeners": memory_summary["known_listeners"]
        }


# Convenience functions for quick access

def create_dj_helper(
    hive_path: Path | None = None,
    agent_md_path: Path | str | None = None
) -> DJBroadcastHelper:
    """
    Create a DJ broadcast helper instance.
    
    Args:
        hive_path: Path to hive directory
        agent_md_path: Path to Agent.md
        
    Returns:
        DJBroadcastHelper instance
    """
    return DJBroadcastHelper(hive_path, agent_md_path)


def get_dj_context_for_time(time_of_day: str) -> str:
    """
    Quick function to get DJ context for a specific time of day.
    
    Args:
        time_of_day: morning, afternoon, or evening
        
    Returns:
        Context string for broadcast
    """
    helper = DJBroadcastHelper()
    return helper.start_session(time_of_day=time_of_day)
