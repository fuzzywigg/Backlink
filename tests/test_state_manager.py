"""Unit tests for LIVE hive.utils.state_manager.StateManager.

Covers HMAC envelope write/read, legacy unsigned state, and secret-key
gating — FILE storage only, no network.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from pathlib import Path

import pytest

from hive.utils.state_manager import StateManager


@pytest.fixture
def hive_root(tmp_path: Path) -> Path:
    """Honeycomb root matching StateManager's hive_path / honeycomb layout."""
    (tmp_path / "honeycomb").mkdir()
    return tmp_path


@pytest.mark.unit
class TestStateManagerSecrets:
    """Secret key resolution for prod vs explicit test/dev."""

    def test_requires_secret_outside_dev(
        self, hive_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("HIVE_SECRET_KEY", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "production")
        with pytest.raises(ValueError, match="HIVE_SECRET_KEY"):
            StateManager(hive_path=hive_root)

    def test_dev_environment_allows_default_key(
        self, hive_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("HIVE_SECRET_KEY", raising=False)
        monkeypatch.setenv("ENVIRONMENT", "test")
        manager = StateManager(hive_path=hive_root)
        assert manager.secret_key == b"dev_secret_key_change_me_in_prod"

    def test_explicit_secret_key_used(
        self, hive_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("HIVE_SECRET_KEY", "ci_test_secret")
        manager = StateManager(hive_path=hive_root)
        assert manager.secret_key == b"ci_test_secret"


@pytest.mark.unit
class TestStateManagerSigning:
    """HMAC envelope write/read paths."""

    def test_write_state_creates_signed_envelope(
        self, hive_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("HIVE_SECRET_KEY", "sign_me")
        monkeypatch.setenv("STORAGE_TYPE", "FILE")
        manager = StateManager(hive_path=hive_root)

        manager.write_state({"persona": "morning"}, bee_type="dj_bee")

        raw = json.loads((hive_root / "honeycomb" / "state.json").read_text(encoding="utf-8"))
        assert "signature" in raw
        assert raw["ver"] == "1.0"
        assert raw["data"]["persona"] == "morning"
        assert raw["data"]["_meta"]["last_updated_by"] == "dj_bee"
        assert "last_updated" in raw["data"]["_meta"]

        expected = hmac.new(
            b"sign_me",
            json.dumps(raw["data"], sort_keys=True).encode(),
            hashlib.sha256,
        ).hexdigest()
        assert raw["signature"] == expected

    def test_read_state_returns_inner_data(
        self, hive_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("HIVE_SECRET_KEY", "sign_me")
        monkeypatch.setenv("STORAGE_TYPE", "FILE")
        manager = StateManager(hive_path=hive_root)
        manager.write_state({"alerts": []}, bee_type="stream_monitor")

        data = manager.read_state()
        assert data["alerts"] == []
        assert data["_meta"]["last_updated_by"] == "stream_monitor"
        assert "signature" not in data

    def test_read_missing_state_returns_empty(
        self, hive_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("HIVE_SECRET_KEY", "sign_me")
        manager = StateManager(hive_path=hive_root)
        assert manager.read_state() == {}

    def test_legacy_unsigned_state_returned_as_is(
        self, hive_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("HIVE_SECRET_KEY", "sign_me")
        legacy = {"persona": "evening", "current_track": None}
        (hive_root / "honeycomb" / "state.json").write_text(json.dumps(legacy), encoding="utf-8")
        manager = StateManager(hive_path=hive_root)
        assert manager.read_state() == legacy

    def test_sign_data_is_deterministic(
        self, hive_root: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("HIVE_SECRET_KEY", "stable")
        manager = StateManager(hive_path=hive_root)
        payload = {"b": 2, "a": 1}
        assert manager._sign_data(payload) == manager._sign_data({"a": 1, "b": 2})
