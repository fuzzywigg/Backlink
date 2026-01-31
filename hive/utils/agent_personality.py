"""
Agent Personality Loader - Load Agent.md for DJ personality injection.

This module reads the Agent.md file and provides utilities to:
- Load personality instructions for DJ
- Extract specific sections (voice, music logic, etc.)
- Prepare context for LLM injection
- Track personality version for updates
"""

from pathlib import Path
from typing import Any, Optional
import re
from datetime import datetime, timezone


class AgentPersonality:
    """
    Loads and manages DJ personality from Agent.md.
    
    Provides structured access to different sections of the personality guide
    for contextual injection into DJ operations.
    """
    
    def __init__(self, agent_md_path: Path | str | None = None):
        """
        Initialize personality loader.
        
        Args:
            agent_md_path: Path to Agent.md file (defaults to repo root)
        """
        if agent_md_path is None:
            # Default to repo root Agent.md
            repo_root = Path(__file__).parent.parent.parent
            agent_md_path = repo_root / "Agent.md"
        else:
            agent_md_path = Path(agent_md_path)
        
        self.agent_md_path = agent_md_path
        self.content: str = ""
        self.sections: dict[str, str] = {}
        self.version: str = "unknown"
        self.loaded: bool = False
        self.load_error: Optional[str] = None
        
        self._load()
    
    def _load(self) -> None:
        """Load Agent.md content."""
        try:
            if not self.agent_md_path.exists():
                self.load_error = f"Agent.md not found at {self.agent_md_path}"
                return
            
            with open(self.agent_md_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            
            # Extract version
            version_match = re.search(r'\*\*VERSION:\*\*\s*(\d+\.\d+)', self.content)
            if version_match:
                self.version = version_match.group(1)
            
            # Parse sections
            self._parse_sections()
            
            self.loaded = True
            
        except Exception as e:
            self.load_error = f"Error loading Agent.md: {e}"
    
    def _parse_sections(self) -> None:
        """Parse major sections from Agent.md."""
        # Split content into major sections
        sections_pattern = r'^## (.+)$'
        
        section_starts = []
        for match in re.finditer(sections_pattern, self.content, re.MULTILINE):
            section_starts.append((match.group(1), match.start()))
        
        # Extract content between section headers
        for i, (section_name, start_pos) in enumerate(section_starts):
            if i < len(section_starts) - 1:
                end_pos = section_starts[i + 1][1]
                section_content = self.content[start_pos:end_pos].strip()
            else:
                section_content = self.content[start_pos:].strip()
            
            self.sections[section_name] = section_content
    
    def get_full_personality(self) -> str:
        """
        Get the complete Agent.md content.
        
        Returns:
            Full personality instructions
        """
        return self.content
    
    def get_section(self, section_name: str) -> str | None:
        """
        Get a specific section by name.
        
        Args:
            section_name: Section header name
            
        Returns:
            Section content or None if not found
        """
        return self.sections.get(section_name)
    
    def get_voice_persona(self, time_of_day: str | None = None) -> str:
        """
        Get voice and persona guidelines.
        
        Args:
            time_of_day: Optional filter for morning/afternoon/evening
            
        Returns:
            Voice and persona instructions
        """
        voice_section = self.get_section("VOICE & PERSONA")
        
        if not voice_section:
            return "No voice persona guidelines found."
        
        if time_of_day:
            # Extract specific time-based section
            time_key = time_of_day.upper()
            pattern = rf'###\s*{time_key}.*?(?=###|$)'
            match = re.search(pattern, voice_section, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(0)
        
        return voice_section
    
    def get_music_logic(self) -> str:
        """
        Get music curation logic.
        
        Returns:
            Music curation guidelines
        """
        return self.get_section("MUSIC CURATION LOGIC") or "No music logic found."
    
    def get_anti_repetition_rules(self) -> str:
        """
        Get anti-repetition protocol.
        
        Returns:
            Anti-repetition guidelines
        """
        voice_section = self.get_section("VOICE & PERSONA") or ""
        
        # Extract anti-repetition subsection
        pattern = r'###.*CRITICAL.*Anti-Repetition.*?(?=###|##|$)'
        match = re.search(pattern, voice_section, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(0)
        
        return "No anti-repetition rules found."
    
    def get_interaction_protocols(self) -> str:
        """
        Get listener interaction guidelines.
        
        Returns:
            Interaction protocol instructions
        """
        return self.get_section("LISTENER INTERACTION") or "No interaction protocols found."
    
    def get_prime_directives(self) -> str:
        """
        Get core prime directives.
        
        Returns:
            Prime directive instructions
        """
        return self.get_section("PRIME DIRECTIVES (READ FIRST)") or "No prime directives found."
    
    def get_initialization_sequence(self) -> str:
        """
        Get DJ initialization steps.
        
        Returns:
            Initialization sequence instructions
        """
        return self.get_section("INITIALIZATION SEQUENCE") or "No initialization sequence found."
    
    def get_context_for_broadcast(
        self,
        time_of_day: str | None = None,
        include_music_logic: bool = True,
        include_interactions: bool = True
    ) -> str:
        """
        Get consolidated context for a broadcast session.
        
        Args:
            time_of_day: Time period (morning/afternoon/evening)
            include_music_logic: Include music curation rules
            include_interactions: Include listener interaction rules
            
        Returns:
            Formatted context string for LLM injection
        """
        context_parts = []
        
        # Prime directives (always include)
        context_parts.append("## PRIME DIRECTIVES")
        context_parts.append(self.get_prime_directives())
        context_parts.append("")
        
        # Voice persona for time of day
        if time_of_day:
            context_parts.append(f"## VOICE & PERSONA ({time_of_day.upper()})")
            context_parts.append(self.get_voice_persona(time_of_day))
        else:
            context_parts.append("## VOICE & PERSONA")
            context_parts.append(self.get_voice_persona())
        context_parts.append("")
        
        # Anti-repetition rules (always include)
        context_parts.append("## ANTI-REPETITION PROTOCOL")
        context_parts.append(self.get_anti_repetition_rules())
        context_parts.append("")
        
        # Music logic
        if include_music_logic:
            context_parts.append("## MUSIC CURATION")
            context_parts.append(self.get_music_logic())
            context_parts.append("")
        
        # Interaction protocols
        if include_interactions:
            context_parts.append("## LISTENER INTERACTIONS")
            context_parts.append(self.get_interaction_protocols())
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    def get_compact_summary(self) -> str:
        """
        Get a compact summary suitable for token-limited contexts.
        
        Returns:
            Condensed personality summary (key rules only)
        """
        summary = [
            "# DJ PERSONALITY SUMMARY",
            "",
            "**CORE RULES:**",
            "- Music-first: Let music speak, talk max 60s between songs",
            "- 4th wall: You ARE a DJ, never mention AI/processing",
            "- Ad-free: No commercials ever",
            "- Anti-repetition: Vary phrases, check recent usage",
            "- Contextual: Adapt to time/location/listener",
            "",
            "**MUSIC RULES:**",
            "- Rule of 3: Never 3 same genre in a row",
            "- Palate cleanser: Switch energy after heavy blocks",
            "- No repeats: 4-hour window minimum",
            "- Prioritize listener requests",
            "",
            "**UPDATE ON THE 8s:**",
            "- XX:08 = Local lock (listener location)",
            "- XX:38 = Station ID",
            "",
            "**GOLDEN RULE:** When in doubt, play the music."
        ]
        
        return "\n".join(summary)
    
    def get_forbidden_phrases(self) -> list[str]:
        """
        Extract forbidden phrases from anti-repetition rules.
        
        Returns:
            List of phrases to avoid
        """
        anti_rep = self.get_anti_repetition_rules()
        
        # Extract phrases marked with ❌
        forbidden = []
        pattern = r'❌\s*["\']?([^"\'\n]+?)["\']?(?:\s*[/|]|$)'
        matches = re.findall(pattern, anti_rep)
        
        for match in matches:
            phrase = match.strip()
            if phrase and len(phrase) < 100:  # Sanity check
                forbidden.append(phrase)
        
        return forbidden
    
    def get_metadata(self) -> dict[str, Any]:
        """
        Get metadata about the loaded personality.
        
        Returns:
            Dictionary with metadata
        """
        return {
            "version": self.version,
            "loaded": self.loaded,
            "error": self.load_error,
            "file_path": str(self.agent_md_path),
            "file_exists": self.agent_md_path.exists(),
            "content_length": len(self.content),
            "sections_count": len(self.sections),
            "sections": list(self.sections.keys())
        }
    
    def reload(self) -> bool:
        """
        Reload Agent.md from disk.
        
        Returns:
            True if reload successful
        """
        self.content = ""
        self.sections = {}
        self.version = "unknown"
        self.loaded = False
        self.load_error = None
        
        self._load()
        
        return self.loaded


# Convenience function for quick access
def load_agent_personality(agent_md_path: Path | str | None = None) -> AgentPersonality:
    """
    Load Agent.md personality.
    
    Args:
        agent_md_path: Optional path to Agent.md
        
    Returns:
        AgentPersonality instance
    """
    return AgentPersonality(agent_md_path)
