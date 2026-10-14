"""Unit tests for LIVE hive.utils.keys.KeyManager.

Covers env-var priority and keys.json fallback with temp fixtures —
no real secrets or network.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from hive.utils.keys import KeyManager


@pytest.mark.unit
class TestKeyManager:
    """KeyManager.get_key() resolution order."""

    def test_prefers_environment_variable(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        keys_file = tmp_path / "keys.json"
        keys_file.write_text(json.dumps({"MY_KEY": "from_file"}), encoding="utf-8")
        monkeypatch.setenv("MY_KEY", "from_env")

        km = KeyManager(hive_path=str(tmp_path))
        assert km.get_key("MY_KEY") == "from_env"

    def test_falls_back_to_keys_json(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        keys_file = tmp_path / "keys.json"
        keys_file.write_text(json.dumps({"FILE_ONLY": "file_secret"}), encoding="utf-8")
        monkeypatch.delenv("FILE_ONLY", raising=False)

        km = KeyManager(hive_path=str(tmp_path))
        assert km.get_key("FILE_ONLY") == "file_secret"

    def test_missing_key_returns_none(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("MISSING_KEY", raising=False)
        km = KeyManager(hive_path=str(tmp_path))
        assert km.get_key("MISSING_KEY") is None

    def test_corrupt_keys_json_yields_empty_local(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        keys_file = tmp_path / "keys.json"
        keys_file.write_text("{not-json", encoding="utf-8")
        monkeypatch.delenv("ANY_KEY", raising=False)

        km = KeyManager(hive_path=str(tmp_path))
        assert km._local_keys == {}
        assert km.get_key("ANY_KEY") is None

    def test_default_hive_path_points_at_package_parent(self) -> None:
        km = KeyManager()
        assert km.hive_path.name == "hive"
        assert km.keys_path == km.hive_path / "keys.json"
