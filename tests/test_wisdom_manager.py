"""Unit tests for LIVE hive.utils.wisdom_manager.WisdomManager.

Covers wisdom store bootstrap, retrieval, constraint/episode commits, and
episode bounding — graph sync mocked off, no network.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hive.utils.wisdom_manager import WisdomManager


@pytest.fixture
def wisdom_hive(tmp_path: Path) -> Path:
    """Repo-root-shaped path: hive_path/hive/honeycomb for WisdomManager."""
    honeycomb = tmp_path / "hive" / "honeycomb"
    honeycomb.mkdir(parents=True)
    return tmp_path


def _manager(hive_path: Path) -> WisdomManager:
    """Build WisdomManager with graph sync disabled."""
    mgr = WisdomManager(hive_path)
    mgr.graph = None
    return mgr


@pytest.mark.unit
class TestWisdomManagerBootstrap:
    """Genesis wisdom.json creation."""

    def test_creates_wisdom_store_when_missing(self, wisdom_hive: Path) -> None:
        mgr = _manager(wisdom_hive)
        assert mgr.wisdom_path.is_file()
        data = json.loads(mgr.wisdom_path.read_text(encoding="utf-8"))
        assert data["integrity_hash"] == "genesis"
        assert "episodes" in data
        assert data["theology"]["core_tenets"]

    def test_get_relevant_wisdom_returns_theology_and_constraints(self, wisdom_hive: Path) -> None:
        mgr = _manager(wisdom_hive)
        result = mgr.get_relevant_wisdom(context_tags=["music"])
        assert "constraints" in result
        assert "theology" in result
        assert "Broadcast" in result["theology"]["core_tenets"][0]


@pytest.mark.unit
class TestWisdomManagerLessons:
    """Constraint and episode mutation paths."""

    def test_add_constraint_lesson(self, wisdom_hive: Path) -> None:
        mgr = _manager(wisdom_hive)
        mgr.add_lesson(
            {
                "type": "constraint",
                "content": "Never break the fourth wall on air",
                "source": "ConstitutionalAuditorBee",
                "context": "broadcast",
            }
        )
        wisdom = mgr.get_relevant_wisdom()
        contents = [c["content"] for c in wisdom["constraints"]]
        assert "Never break the fourth wall on air" in contents

    def test_duplicate_constraint_not_added_twice(self, wisdom_hive: Path) -> None:
        mgr = _manager(wisdom_hive)
        lesson = {
            "type": "constraint",
            "content": "Keep ads off the main deck",
            "source": "Auditor",
            "context": "monetization",
        }
        mgr.add_lesson(lesson)
        mgr.add_lesson(lesson)
        wisdom = mgr.get_relevant_wisdom()
        matches = [c for c in wisdom["constraints"] if c["content"] == lesson["content"]]
        assert len(matches) == 1

    def test_add_episode_lesson(self, wisdom_hive: Path) -> None:
        mgr = _manager(wisdom_hive)
        mgr.add_lesson(
            {
                "type": "episode",
                "content": "Listener loved the midnight lo-fi block",
                "source": "EngagementBee",
            }
        )
        raw = json.loads(mgr.wisdom_path.read_text(encoding="utf-8"))
        assert len(raw["episodes"]) == 1
        assert "midnight lo-fi" in raw["episodes"][0]["content"]
        assert "timestamp" in raw["episodes"][0]
        assert "last_updated" in raw

    def test_episodes_bounded_to_one_hundred(self, wisdom_hive: Path) -> None:
        mgr = _manager(wisdom_hive)
        for i in range(105):
            mgr.add_lesson(
                {
                    "type": "episode",
                    "content": f"episode-{i}",
                    "source": "test",
                }
            )
        raw = json.loads(mgr.wisdom_path.read_text(encoding="utf-8"))
        assert len(raw["episodes"]) == 100
        assert raw["episodes"][0]["content"] == "episode-5"
        assert raw["episodes"][-1]["content"] == "episode-104"

    def test_corrupt_wisdom_read_returns_empty_collections(self, wisdom_hive: Path) -> None:
        mgr = _manager(wisdom_hive)
        mgr.wisdom_path.write_text("{broken", encoding="utf-8")
        data = mgr._read_wisdom()
        assert data == {"global_constraints": [], "episodes": []}
