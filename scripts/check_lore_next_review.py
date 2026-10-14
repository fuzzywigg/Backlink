#!/usr/bin/env python3
"""Fail if any docs/lore/*.md has a Next Review date in the past.

Stdlib only. Intended for CI and local pre-merge checks so lore document
control cannot silently expire again.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

NEXT_REVIEW_RE = re.compile(
    r"\|\s*\*\*Next Review\*\*\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class LoreReviewFinding:
    """One Next Review date found in a lore markdown file."""

    path: Path
    next_review: date


def repo_root() -> Path:
    """Return the repository root (parent of scripts/)."""
    return Path(__file__).resolve().parent.parent


def find_lore_next_reviews(lore_dir: Path) -> list[LoreReviewFinding]:
    """Collect Next Review dates from markdown files under lore_dir."""
    findings: list[LoreReviewFinding] = []
    if not lore_dir.is_dir():
        raise FileNotFoundError(f"Lore directory not found: {lore_dir}")

    for path in sorted(lore_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        for match in NEXT_REVIEW_RE.finditer(text):
            findings.append(
                LoreReviewFinding(
                    path=path,
                    next_review=date.fromisoformat(match.group(1)),
                )
            )
    return findings


def overdue_reviews(
    findings: list[LoreReviewFinding],
    *,
    today: date,
) -> list[LoreReviewFinding]:
    """Return findings whose Next Review date is strictly before today."""
    return [f for f in findings if f.next_review < today]


def check_lore_next_reviews(
    lore_dir: Path | None = None,
    *,
    today: date | None = None,
) -> list[str]:
    """Return human-readable error lines for overdue lore Next Review dates."""
    root = repo_root()
    directory = lore_dir if lore_dir is not None else root / "docs" / "lore"
    as_of = today if today is not None else date.today()
    findings = find_lore_next_reviews(directory)
    bad = overdue_reviews(findings, today=as_of)
    errors: list[str] = []
    for item in bad:
        rel = item.path.relative_to(root) if item.path.is_relative_to(root) else item.path
        errors.append(
            f"{rel}: Next Review {item.next_review.isoformat()} is overdue "
            f"(today={as_of.isoformat()})"
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Exit 1 if any lore Next Review is overdue."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--lore-dir",
        type=Path,
        default=None,
        help="Override docs/lore directory (default: <repo>/docs/lore)",
    )
    parser.add_argument(
        "--today",
        type=str,
        default=None,
        help="Override today's date as YYYY-MM-DD (for tests)",
    )
    args = parser.parse_args(argv)

    today = date.today()
    if args.today is not None:
        today = datetime.strptime(args.today, "%Y-%m-%d").date()

    errors = check_lore_next_reviews(args.lore_dir, today=today)
    if errors:
        print("Lore document-control review overdue:", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        print(
            "Update Document Control (Last Modified, Version, revision history, "
            "Next Review) after a real review.",
            file=sys.stderr,
        )
        return 1

    findings = find_lore_next_reviews(
        args.lore_dir if args.lore_dir is not None else repo_root() / "docs" / "lore"
    )
    print(
        f"OK: {len(findings)} Next Review date(s) in lore are current (as of {today.isoformat()})."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
