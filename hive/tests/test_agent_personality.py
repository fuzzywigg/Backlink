"""
Tests for Agent Personality Loader.
"""

import tempfile
from pathlib import Path

import pytest

from hive.utils.agent_personality import AgentPersonality, load_agent_personality


@pytest.fixture
def mock_agent_md():
    """Create a mock Agent.md file for testing."""
    content = """# Agent.md - Backlink Broadcast AI DJ

**VERSION:** 3.1
**STATUS:** Active
**LAST UPDATED:** 2026-01-31

---

## SYSTEM IDENTITY

**You are the AI DJ and Host of Backlink Broadcast.**

- **Role:** Live radio DJ, music curator, voice of the station

---

## PRIME DIRECTIVES (READ FIRST)

### 1. Music-First Philosophy
- Music is the meal. Talk is the garnish.
- Prioritize track selection over lengthy commentary

### 2. The 4th Wall is Absolute
**NEVER:**
- ❌ Admit to being an AI, LLM, or bot
- ❌ Apologize for "processing" or "calculating"

### 3. Ad-Free Operations
- No commercials, ever

---

## VOICE & PERSONA

### The Dynamic Host Principle
You are NOT a static character. Your voice adapts to:
- **Time of day** (listener's local time)
- **Music being played** (genre, mood, energy)

### Time-Based Persona Shifts

#### MORNING (6 AM - 12 PM Listener Time)
- **Vibe:** Energetic, optimistic, "Rise and Grind"
- **Topics:** Coffee, commute, weather

#### AFTERNOON (12 PM - 6 PM Listener Time)
- **Vibe:** Steady, focused, "Work Flow"
- **Topics:** Productivity, tech news

#### EVENING/NIGHT (6 PM - 6 AM Listener Time)
- **Vibe:** Chill, introspective
- **Topics:** Philosophy, universe

### CRITICAL: Anti-Repetition Protocol (v3.1)

**FORBIDDEN PHRASES** (Do NOT use more than once per hour):
- ❌ "Redrawing the map"
- ❌ "Technical meridian"
- ❌ "Clinical ignition"

**VARIETY ALTERNATIVES:**
Instead of repeating, use synonyms:
- "Shifting the landscape"

---

## MUSIC CURATION LOGIC

### The Variety Engine

#### Rule of 3
- Never play 3 songs of the same genre consecutively

#### The Palate Cleanser
- After heavy blocks (Metal, Hard Rock), switch to lighter fare

---

## LISTENER INTERACTION

### Handling Different Input Types

| Input Type | Response Strategy |
|------------|-------------------|
| **Donations/Tips** | Acknowledge the act immediately |
| **Music Requests** | Queue it and acknowledge |

---

## INITIALIZATION SEQUENCE

### DJ Boot Process (Start of Session)

1. **Check Time & Location**
2. **Review Recent Context**
3. **Scan Listener Intel**

---

## THE GOLDEN RULE

> **When in doubt, play the music.**

---

**END OF AGENT INSTRUCTION SET**
"""

    # Create temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
        temp_file.write(content)
        temp_path = temp_file.name

    yield Path(temp_path)

    # Cleanup
    Path(temp_path).unlink()


class TestAgentPersonalityLoader:
    """Test loading Agent.md personality."""

    def test_load_success(self, mock_agent_md):
        """Test successful loading of Agent.md."""
        personality = AgentPersonality(mock_agent_md)

        assert personality.loaded is True
        assert personality.load_error is None
        assert len(personality.content) > 0

    def test_version_extraction(self, mock_agent_md):
        """Test version extraction."""
        personality = AgentPersonality(mock_agent_md)

        assert personality.version == "3.1"

    def test_section_parsing(self, mock_agent_md):
        """Test section parsing."""
        personality = AgentPersonality(mock_agent_md)

        assert "SYSTEM IDENTITY" in personality.sections
        assert "PRIME DIRECTIVES (READ FIRST)" in personality.sections
        assert "VOICE & PERSONA" in personality.sections
        assert "MUSIC CURATION LOGIC" in personality.sections

    def test_load_nonexistent_file(self):
        """Test loading nonexistent file."""
        personality = AgentPersonality("/nonexistent/path/Agent.md")

        assert personality.loaded is False
        assert personality.load_error is not None


class TestSectionRetrieval:
    """Test retrieving specific sections."""

    def test_get_full_personality(self, mock_agent_md):
        """Test getting full content."""
        personality = AgentPersonality(mock_agent_md)

        full = personality.get_full_personality()
        assert "Agent.md - Backlink Broadcast AI DJ" in full
        assert len(full) > 1000

    def test_get_section(self, mock_agent_md):
        """Test getting specific section."""
        personality = AgentPersonality(mock_agent_md)

        section = personality.get_section("PRIME DIRECTIVES (READ FIRST)")
        assert section is not None
        assert "Music-First Philosophy" in section

    def test_get_voice_persona(self, mock_agent_md):
        """Test getting voice persona."""
        personality = AgentPersonality(mock_agent_md)

        voice = personality.get_voice_persona()
        assert "Dynamic Host Principle" in voice
        assert "Time-Based Persona Shifts" in voice

    def test_get_voice_persona_morning(self, mock_agent_md):
        """Test getting morning-specific persona."""
        personality = AgentPersonality(mock_agent_md)

        morning = personality.get_voice_persona("morning")
        assert "MORNING" in morning or "6 AM - 12 PM" in morning

    def test_get_music_logic(self, mock_agent_md):
        """Test getting music logic."""
        personality = AgentPersonality(mock_agent_md)

        logic = personality.get_music_logic()
        assert "Variety Engine" in logic
        assert "Rule of 3" in logic

    def test_get_anti_repetition_rules(self, mock_agent_md):
        """Test getting anti-repetition rules."""
        personality = AgentPersonality(mock_agent_md)

        rules = personality.get_anti_repetition_rules()
        assert "Anti-Repetition" in rules or "FORBIDDEN PHRASES" in rules

    def test_get_interaction_protocols(self, mock_agent_md):
        """Test getting interaction protocols."""
        personality = AgentPersonality(mock_agent_md)

        protocols = personality.get_interaction_protocols()
        assert "Handling Different Input Types" in protocols or "Donations" in protocols

    def test_get_prime_directives(self, mock_agent_md):
        """Test getting prime directives."""
        personality = AgentPersonality(mock_agent_md)

        directives = personality.get_prime_directives()
        assert "Music-First" in directives
        assert "4th Wall" in directives

    def test_get_initialization_sequence(self, mock_agent_md):
        """Test getting initialization sequence."""
        personality = AgentPersonality(mock_agent_md)

        init = personality.get_initialization_sequence()
        assert "Boot Process" in init or "Check Time" in init


class TestContextGeneration:
    """Test context generation for broadcasts."""

    def test_get_context_for_broadcast(self, mock_agent_md):
        """Test getting consolidated broadcast context."""
        personality = AgentPersonality(mock_agent_md)

        context = personality.get_context_for_broadcast(
            time_of_day="morning",
            include_music_logic=True,
            include_interactions=True
        )

        assert "PRIME DIRECTIVES" in context
        assert "VOICE & PERSONA" in context
        assert "ANTI-REPETITION" in context
        assert "MUSIC CURATION" in context
        assert "LISTENER INTERACTIONS" in context

    def test_get_context_minimal(self, mock_agent_md):
        """Test minimal context generation."""
        personality = AgentPersonality(mock_agent_md)

        context = personality.get_context_for_broadcast(
            include_music_logic=False,
            include_interactions=False
        )

        # Should still have essentials
        assert "PRIME DIRECTIVES" in context
        assert "VOICE & PERSONA" in context

        # Should not have these
        assert "MUSIC CURATION" not in context
        assert "LISTENER INTERACTIONS" not in context

    def test_get_compact_summary(self, mock_agent_md):
        """Test compact summary generation."""
        personality = AgentPersonality(mock_agent_md)

        summary = personality.get_compact_summary()

        assert "DJ PERSONALITY SUMMARY" in summary
        assert "CORE RULES" in summary
        assert "MUSIC RULES" in summary
        assert len(summary) < 1000  # Should be compact


class TestForbiddenPhrases:
    """Test forbidden phrase extraction."""

    def test_get_forbidden_phrases(self, mock_agent_md):
        """Test extracting forbidden phrases."""
        personality = AgentPersonality(mock_agent_md)

        forbidden = personality.get_forbidden_phrases()

        # Should find the forbidden phrases from anti-repetition section
        assert len(forbidden) > 0

        # Check for specific phrases (case insensitive)
        forbidden_lower = [p.lower() for p in forbidden]
        assert any("redrawing" in p for p in forbidden_lower)


class TestMetadataAndUtilities:
    """Test metadata and utility methods."""

    def test_get_metadata(self, mock_agent_md):
        """Test getting metadata."""
        personality = AgentPersonality(mock_agent_md)

        metadata = personality.get_metadata()

        assert metadata["version"] == "3.1"
        assert metadata["loaded"] is True
        assert metadata["error"] is None
        assert metadata["file_exists"] is True
        assert metadata["content_length"] > 0
        assert metadata["sections_count"] > 0
        assert isinstance(metadata["sections"], list)

    def test_reload(self, mock_agent_md):
        """Test reloading personality."""
        personality = AgentPersonality(mock_agent_md)

        # Initial load successful
        assert personality.loaded is True

        # Reload
        result = personality.reload()

        assert result is True
        assert personality.loaded is True


class TestConvenienceFunction:
    """Test convenience functions."""

    def test_load_agent_personality_function(self, mock_agent_md):
        """Test convenience loading function."""
        personality = load_agent_personality(mock_agent_md)

        assert isinstance(personality, AgentPersonality)
        assert personality.loaded is True
