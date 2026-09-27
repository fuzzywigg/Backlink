"""Unit tests for LIVE core_utils.ontology_manager.OntologyManager.

Covers library load/fallback, hour-quadrant rotation, and validate_text
scoring — no network or Gemini.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from core_utils.ontology_manager import OntologyManager

SAMPLE_LIBRARY = {
    "meta": {"version": "1.0"},
    "ontologies": {
        "cyber_noir": {
            "id": "cyber_noir",
            "vibe": "Dark",
            "banned_words": ["synergy", "sunshine"],
            "prompt_injection": "Speak like a pirate radio hacker.",
        },
        "solar_punk": {
            "id": "solar_punk",
            "vibe": "Optimistic",
            "banned_words": ["darkness"],
            "prompt_injection": "Channel renewable energy.",
        },
        "high_tech": {
            "id": "high_tech",
            "vibe": "Precise",
            "banned_words": ["vibes", "chill"],
            "prompt_injection": "Be analytical.",
        },
        "abstract_flow": {
            "id": "abstract_flow",
            "vibe": "Philosophical",
            "banned_words": ["roadmap"],
            "prompt_injection": "Find the rhythm.",
        },
    },
}


@pytest.fixture
def library_path(tmp_path: Path) -> Path:
    path = tmp_path / "ontology_library.json"
    path.write_text(json.dumps(SAMPLE_LIBRARY), encoding="utf-8")
    return path


@pytest.mark.unit
class TestLoadLibrary:
    """_load_library() missing/corrupt/valid paths."""

    def test_missing_file_yields_empty_library(self, tmp_path: Path) -> None:
        missing = tmp_path / "does_not_exist.json"
        manager = OntologyManager(library_path=str(missing))
        assert manager.library == {}
        assert manager.current_ontology is None

    def test_corrupt_json_yields_empty_library(self, tmp_path: Path) -> None:
        bad = tmp_path / "broken.json"
        bad.write_text("{not-json", encoding="utf-8")
        manager = OntologyManager(library_path=str(bad))
        assert manager.library == {}

    def test_valid_library_loads(self, library_path: Path) -> None:
        manager = OntologyManager(library_path=str(library_path))
        assert "ontologies" in manager.library
        assert "cyber_noir" in manager.library["ontologies"]


@pytest.mark.unit
class TestGetCurrentOntology:
    """Hour-quadrant selection, offset, override, and fallback."""

    @pytest.mark.parametrize(
        ("hour", "expected_id"),
        [
            (0, "cyber_noir"),
            (5, "cyber_noir"),
            (6, "solar_punk"),
            (11, "solar_punk"),
            (12, "high_tech"),
            (17, "high_tech"),
            (18, "abstract_flow"),
            (23, "abstract_flow"),
        ],
    )
    def test_quadrant_by_override_hour(
        self, library_path: Path, hour: int, expected_id: str
    ) -> None:
        manager = OntologyManager(library_path=str(library_path))
        ontology = manager.get_current_ontology(override_hour=hour)
        assert ontology["id"] == expected_id
        assert manager.current_ontology is ontology

    def test_offset_hour_wraps_modulo_24(self, library_path: Path) -> None:
        manager = OntologyManager(library_path=str(library_path))
        # override 22 + offset 4 => hour 2 => cyber_noir
        ontology = manager.get_current_ontology(offset_hour=4, override_hour=22)
        assert ontology["id"] == "cyber_noir"

    def test_missing_ontologies_key_returns_fallback(self, tmp_path: Path) -> None:
        path = tmp_path / "empty_meta.json"
        path.write_text(json.dumps({"meta": {}}), encoding="utf-8")
        manager = OntologyManager(library_path=str(path))
        ontology = manager.get_current_ontology(override_hour=3)
        assert ontology["id"] == "fallback"
        assert ontology["vibe"] == "Neutral"
        assert "Speak clearly" in ontology["prompt_injection"]

    def test_unknown_quadrant_key_returns_fallback(self, tmp_path: Path) -> None:
        path = tmp_path / "partial.json"
        path.write_text(
            json.dumps({"ontologies": {"only_other": {"id": "only_other"}}}),
            encoding="utf-8",
        )
        manager = OntologyManager(library_path=str(path))
        ontology = manager.get_current_ontology(override_hour=3)
        assert ontology["id"] == "fallback"

    def test_default_path_loads_repo_library(self) -> None:
        manager = OntologyManager()
        ontology = manager.get_current_ontology(override_hour=9)
        assert ontology["id"] == "solar_punk"
        assert "banned_words" in ontology


@pytest.mark.unit
class TestValidateText:
    """validate_text() empty / banned / fresh scoring."""

    def test_empty_text_scores_zero(self, library_path: Path) -> None:
        manager = OntologyManager(library_path=str(library_path))
        manager.get_current_ontology(override_hour=3)
        assert manager.validate_text("", []) == 0.0

    def test_banned_word_scores_penalty(self, library_path: Path) -> None:
        manager = OntologyManager(library_path=str(library_path))
        manager.get_current_ontology(override_hour=3)  # cyber_noir
        score = manager.validate_text("Tonight we chase synergy in the neon.", [])
        assert score == 0.5

    def test_banned_word_match_is_case_insensitive(self, library_path: Path) -> None:
        manager = OntologyManager(library_path=str(library_path))
        manager.get_current_ontology(override_hour=3)
        assert manager.validate_text("SUNSHINE forever", []) == 0.5

    def test_clean_text_scores_fresh(self, library_path: Path) -> None:
        manager = OntologyManager(library_path=str(library_path))
        manager.get_current_ontology(override_hour=3)
        score = manager.validate_text("Decrypt the neon pulse through static rain.", [])
        assert score == 1.0

    def test_no_current_ontology_skips_banned_check(self, library_path: Path) -> None:
        manager = OntologyManager(library_path=str(library_path))
        assert manager.current_ontology is None
        # Without selecting an ontology, banned-word path is skipped
        assert manager.validate_text("synergy sunshine vibes", []) == 1.0
