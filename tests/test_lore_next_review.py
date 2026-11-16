"""Tests for lore Next Review document-control guard."""

from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest

from scripts.check_lore_next_review import (
    check_lore_next_reviews,
    find_lore_next_reviews,
    overdue_reviews,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
LORE_DIR = REPO_ROOT / "docs" / "lore"


def test_live_lore_next_reviews_not_past() -> None:
    """CI guard: docs/lore/*.md Next Review dates must not be in the past."""
    errors = check_lore_next_reviews(LORE_DIR, today=date.today())
    assert errors == [], "\n".join(errors)


def test_finds_next_review_in_fixture(tmp_path: Path) -> None:
    """Parser extracts ISO Next Review dates from Document Control tables."""
    sample = tmp_path / "SAMPLE.md"
    sample.write_text(
        """# Sample

## Document Control

| Property            | Value      |
|---------------------|------------|
| **Next Review**     | 2027-02-20 |
""",
        encoding="utf-8",
    )
    findings = find_lore_next_reviews(tmp_path)
    assert len(findings) == 1
    assert findings[0].next_review == date(2027, 2, 20)


def test_overdue_detection(tmp_path: Path) -> None:
    """Dates strictly before today are overdue; today and future are fine."""
    overdue = tmp_path / "OLD.md"
    overdue.write_text(
        "| **Next Review**     | 2026-06-01 |\n",
        encoding="utf-8",
    )
    current = tmp_path / "OK.md"
    current.write_text(
        "| **Next Review**     | 2027-02-20 |\n",
        encoding="utf-8",
    )
    findings = find_lore_next_reviews(tmp_path)
    bad = overdue_reviews(findings, today=date(2026, 8, 20))
    assert [f.path.name for f in bad] == ["OLD.md"]


def test_files_without_next_review_are_ignored(tmp_path: Path) -> None:
    """Lore files without a Next Review block do not fail the check."""
    (tmp_path / "NO_CONTROL.md").write_text("# Persona\n\nNo control block.\n", encoding="utf-8")
    assert find_lore_next_reviews(tmp_path) == []
    assert check_lore_next_reviews(tmp_path, today=date(2026, 8, 20)) == []


def test_missing_lore_dir_raises(tmp_path: Path) -> None:
    """Missing lore directory is a hard error, not a silent pass."""
    with pytest.raises(FileNotFoundError):
        find_lore_next_reviews(tmp_path / "missing")
