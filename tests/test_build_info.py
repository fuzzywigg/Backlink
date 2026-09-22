"""
Tests for non-secret build/source provenance helpers.
"""

import pytest

from hive.utils.build_info import resolve_build_id, resolve_build_time, resolve_git_sha


@pytest.fixture(autouse=True)
def _clear_provenance_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure provenance env vars do not leak across tests."""
    for key in (
        "GIT_SHA",
        "SOURCE_COMMIT",
        "COMMIT_SHA",
        "BUILD_ID",
        "BUILD_TIME",
        "BUILD_TIMESTAMP",
    ):
        monkeypatch.delenv(key, raising=False)


class TestResolveGitSha:
    """resolve_git_sha() env precedence and fallback."""

    def test_fallback_unknown_when_unset(self) -> None:
        assert resolve_git_sha() == "unknown"

    def test_prefers_git_sha(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GIT_SHA", "deadbeef")
        monkeypatch.setenv("SOURCE_COMMIT", "other")
        monkeypatch.setenv("COMMIT_SHA", "cloud")
        assert resolve_git_sha() == "deadbeef"

    def test_falls_back_to_source_commit(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SOURCE_COMMIT", "source123")
        assert resolve_git_sha() == "source123"

    def test_falls_back_to_commit_sha(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("COMMIT_SHA", "cloudsha")
        assert resolve_git_sha() == "cloudsha"

    def test_ignores_whitespace_only(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("GIT_SHA", "   ")
        monkeypatch.setenv("COMMIT_SHA", "realsha")
        assert resolve_git_sha() == "realsha"


class TestResolveBuildId:
    """resolve_build_id() behavior."""

    def test_none_when_unset(self) -> None:
        assert resolve_build_id() is None

    def test_returns_build_id(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUILD_ID", "12345")
        assert resolve_build_id() == "12345"


class TestResolveBuildTime:
    """resolve_build_time() behavior."""

    def test_none_when_unset(self) -> None:
        assert resolve_build_time() is None

    def test_prefers_build_time(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUILD_TIME", "2026-03-22T12:00:00Z")
        monkeypatch.setenv("BUILD_TIMESTAMP", "legacy")
        assert resolve_build_time() == "2026-03-22T12:00:00Z"

    def test_falls_back_to_build_timestamp(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("BUILD_TIMESTAMP", "20251228_05")
        assert resolve_build_time() == "20251228_05"
