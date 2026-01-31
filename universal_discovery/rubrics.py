from abc import ABC, abstractmethod


class Rubric(ABC):
    @abstractmethod
    def evaluate(self, content_summary: str) -> dict:
        """Returns a score dict and analysis."""
        pass

class GenericSME(Rubric):
    def evaluate(self, content_summary: str) -> dict:
        # Placeholder logic - in real usage, this might call an LLM
        return {
            "scores": {
                "Utility": 5,
                "Quality": 5,
                "Relevance": 5,
                "Safety": 10
            },
            "analysis": "Generic analysis placeholder. This resource appears to be standard content."
        }

class SovereignAI(Rubric):
    def evaluate(self, content_summary: str) -> dict:
        # Placeholder logic
        return {
            "scores": {
                "strategic": 0,
                "sovereign": 0,
                "agentic": 0,
                "technical": 0
            },
            "analysis": "Sovereign analysis placeholder. Needs deeper inspection."
        }

class StrictAgnostic(Rubric):
    def evaluate(self, content_summary: str) -> dict:
        return {
            "scores": {
                "Focus": 0,       # How well it sticks to the specific task
                "Depth": 0,       # Technical depth relative to subject
                "Clarity": 0,     # Absence of fluff
                "Utility": 0      # Direct usefulness
            },
            "analysis": "Strict evaluation. Only high-focus, high-depth items pass."
        }

def get_rubric(name: str) -> Rubric:
    if name == "sovereign_ai":
        return SovereignAI()
    if name == "strict_agnostic":
        return StrictAgnostic()
    return GenericSME()
