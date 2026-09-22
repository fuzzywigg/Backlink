# DJ Memory & Agent Integration System

## Overview

This document describes the DJ memory and personality integration system that provides context and awareness to support autonomous DJ operations.

**Philosophy:** The system provides memory, context, and suggestions to inform DJ decisions—not enforce rigid rules. The DJ is trusted to use professional judgment, just like any experienced broadcaster.

## New Modules

### 1. DJ Memory Manager (`hive/utils/dj_memory.py`)

Tracks context and history to help the DJ make informed decisions.

**Features:**
- Song playback history tracking (last 100 plays)
- Listener profile management
- Language pattern tracking for awareness
- Session context storage
- Genre distribution analytics
- Time-window based queries

**Purpose:** Provides awareness and context, not enforcement. The DJ uses this information to make autonomous, informed decisions.

**Usage:**
```python
from hive.utils.dj_memory import DJMemory

memory = DJMemory()

# Track songs
memory.track_song_played("Song Title", "Artist", genre="Rock", mood="Energetic")

# Check if song was played recently (4-hour window)
was_recent = memory.was_song_played_recently("Song Title", "Artist", hours=4)

# Remember listeners
memory.remember_listener("listener_123", name="John", location="Seattle")

# Track phrases for anti-repetition
memory.track_phrase_usage("Redrawing the map")
was_used = memory.was_phrase_used_recently("Redrawing the map", hours=1)

# Get memory summary
summary = memory.get_memory_summary()
```

### 2. Agent Personality Loader (`hive/utils/agent_personality.py`)

Loads and parses Agent.md for personality injection into DJ operations.

**Features:**
- Dynamic Agent.md loading
- Section-specific retrieval
- Time-of-day persona extraction
- Forbidden phrase extraction
- Broadcast context generation
- Compact summaries for token-limited contexts

**Usage:**
```python
from hive.utils.agent_personality import AgentPersonality

personality = AgentPersonality()

# Get full personality
full = personality.get_full_personality()

# Get morning-specific persona
morning = personality.get_voice_persona("morning")

# Get music curation logic
music_logic = personality.get_music_logic()

# Get anti-repetition rules
anti_rep = personality.get_anti_repetition_rules()

# Get forbidden phrases
forbidden = personality.get_forbidden_phrases()

# Generate broadcast context
context = personality.get_context_for_broadcast(
    time_of_day="morning", include_music_logic=True, include_interactions=True
)

# Get compact summary (for token limits)
summary = personality.get_compact_summary()
```

### 3. DJ Broadcast Helper (`hive/utils/dj_broadcast_helper.py`)

Unified helper that combines Agent.md personality with DJ memory to provide context for autonomous broadcasting.

**Features:**
- Integrated session management
- Automatic time-of-day detection
- Recent play awareness (not blocking)
- Genre pattern awareness (not enforcement)
- Listener context generation
- Language suggestion (not validation)
- Comprehensive broadcast summaries

**Philosophy:** All checks are **advisory and informational**. The DJ receives context and suggestions but makes final decisions autonomously based on professional judgment.

**Usage:**
```python
from hive.utils.dj_broadcast_helper import DJBroadcastHelper

helper = DJBroadcastHelper()

# Start a session - loads personality context
context = helper.start_session(time_of_day="morning", location="Seattle")
# Use this context to inform LLM about personality and situation

# Track songs for history
helper.track_song_played("Song", "Artist", genre="Rock")

# Check if song was played recently (for awareness, not blocking)
was_recent, note = helper.can_play_song("Song", "Artist", hours=4)
# Returns (True, "Note: played recently") or (False, "Not recently played")
# DJ decides whether to play anyway based on context

# Check genre patterns (for awareness, not enforcement)
has_pattern, note = helper.check_genre_variety("Rock", limit=3)
# Returns (True, "Note: Would be 3 consecutive Rock") or (False, "Variety present")
# DJ decides whether pattern makes sense for the moment

# Get language suggestions (advisory, not blocking)
suggestions = helper.get_content_suggestions("Your broadcast text")
# Returns list of suggestions like "Note: phrase used recently—consider varying"
# Empty list if no suggestions. DJ chooses whether to adjust.

# Remember listeners
helper.remember_listener("id", name="John", location="Seattle")

# Get listener context for personalized moments
context = helper.get_listener_context("id")

# Track phrases for pattern awareness
helper.track_phrase_used("Some phrase")

# Check phrase patterns (for awareness)
was_recent, count = helper.check_phrase_repetition("Some phrase", hours=1)

# Get session summary
summary = helper.get_broadcast_summary()
```

## Integration Points

### For DJ Bees

Integrate memory and personality to provide context for autonomous decisions:

```python
from hive.bees.base_bee import EmployedBee
from hive.utils.dj_broadcast_helper import DJBroadcastHelper


class EnhancedDJBee(EmployedBee):
    def __init__(self, hive_path=None):
        super().__init__(hive_path)
        self.dj_helper = DJBroadcastHelper(hive_path=self.hive_path)

    def work(self, task=None):
        # Start session with personality context
        context = self.dj_helper.start_session(time_of_day=self._get_time_of_day())

        # Use context for LLM injection (provides guidelines, not rules)
        response = self.llm_client.generate(system=context, prompt="Create a morning show intro")

        # Track what was played (builds context)
        self.dj_helper.track_song_played(song_title="Song", artist="Artist", genre="Rock")

        # Get suggestions about content (advisory, not blocking)
        suggestions = self.dj_helper.get_content_suggestions(response)
        if suggestions:
            # DJ can choose to adjust or proceed as-is
            self.log(f"Content suggestions: {suggestions}")

        return {"status": "success"}
```

### For Show Prep Bees

Integrate memory context into show preparation:

```python
from hive.utils.dj_broadcast_helper import DJBroadcastHelper


class EnhancedShowPrepBee(EmployedBee):
    def work(self, task=None):
        helper = DJBroadcastHelper()

        # Get recent song history for variety planning
        recent_songs = helper.memory.get_recent_songs(limit=20)
        genre_dist = helper.memory.get_genre_distribution(hours=2)

        # Get listener profiles for personalized content
        listeners = helper.memory.get_all_listeners(limit=10)

        # Generate talking points with personality context
        personality_context = helper.personality.get_section("VOICE & PERSONA")

        # Ensure no forbidden phrases
        forbidden = helper.get_forbidden_phrases()

        return {
            "talking_points": self._generate_points(context=personality_context, avoid=forbidden)
        }
```

## Testing

Comprehensive test suites have been created:

```bash
# Run DJ Memory tests
pytest hive/tests/test_dj_memory.py -v

# Run Agent Personality tests
pytest hive/tests/test_agent_personality.py -v
```

**Test Coverage:**
- `test_dj_memory.py`: 30+ test cases covering all memory operations
- `test_agent_personality.py`: 25+ test cases covering personality loading

## Demo

A demonstration script is available:

```bash
python examples/dj_integration_demo.py
```

This demonstrates:
- Morning show workflow
- Afternoon transition
- Memory persistence
- Compact summaries
- Anti-repetition validation
- Genre variety checking

## Memory Persistence

All DJ memory is persisted to `hive/honeycomb/dj_memory.json`:

```json
{
  "song_history": [
    {
      "title": "Song Title",
      "artist": "Artist Name",
      "genre": "Rock",
      "mood": "Energetic",
      "played_at": "2026-01-31T14:00:00Z"
    }
  ],
  "listeners": {
    "listener_123": {
      "id": "listener_123",
      "name": "John Doe",
      "location": "Seattle, WA",
      "first_seen": "2026-01-31T14:00:00Z",
      "last_seen": "2026-01-31T15:30:00Z",
      "interactions": 5
    }
  },
  "phrases_used": {
    "redrawing the map": [
      {
        "timestamp": "2026-01-31T14:15:00Z",
        "category": "transition"
      }
    ]
  },
  "session_context": {},
  "metadata": {
    "created_at": "2026-01-31T14:00:00Z",
    "version": "1.0.0"
  }
}
```

## Configuration

No additional configuration required. The system automatically:
- Loads Agent.md from repository root
- Creates memory storage in `hive/honeycomb/`
- Integrates with existing StateManager

## Benefits

### Context Continuity
- DJ remembers past songs and listeners
- No accidental repeats
- Personalized listener interactions

### Personality Consistency
- Agent.md as single source of truth
- Time-based persona switching
- Anti-repetition enforcement

### Operational Efficiency
- Automated variety checking
- Built-in content validation
- Comprehensive session summaries

### Scalability
- Memory limited to last 100 songs (prevents unbounded growth)
- Efficient time-window queries
- Persistent storage for long-running operations

## Key Philosophy: Advisory, Not Prescriptive

**Important:** All validation methods are **advisory and informational**, not blocking:

- `can_play_song()` - Informs about recent plays, doesn't block
- `check_genre_variety()` - Notes patterns, doesn't enforce
- `get_content_suggestions()` - Offers suggestions, doesn't validate/block
- DJ makes final decisions based on professional judgment

This approach:
- Prevents rule conflicts and operational chaos
- Trusts DJ expertise and autonomy
- Provides context without constraints
- Mimics how real radio DJs operate with awareness but autonomy

## Future Enhancements

Planned improvements:
- [ ] Redis backend for distributed memory
- [ ] Advanced analytics and reporting
- [ ] Memory backup/restore utilities
- [ ] Cross-bee memory sharing
- [ ] Real-time memory dashboard

## API Reference

Full API documentation is available in the module docstrings:
- `hive/utils/dj_memory.py` - Complete memory API
- `hive/utils/agent_personality.py` - Personality loading API
- `hive/utils/dj_broadcast_helper.py` - Integrated helper API

## Support

For questions or issues:
1. Check module docstrings for detailed API docs
2. Review test files for usage examples
3. Run the demo script for practical demonstrations
4. Consult AGENT_RECOMMENDATIONS.md for strategic context
