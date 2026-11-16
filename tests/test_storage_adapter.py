"""Unit tests for LIVE hive.utils.storage_adapter.StorageAdapter.

Covers FILE-mode read/write, path-traversal guards, and Firestore
fallback — no network or live GCP calls.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from hive.utils.storage_adapter import StorageAdapter


@pytest.mark.unit
class TestStorageAdapterFileMode:
    """FILE backend round-trips and safety checks."""

    def test_defaults_to_file_storage(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.delenv("STORAGE_TYPE", raising=False)
        adapter = StorageAdapter(tmp_path)
        assert adapter.storage_type == "FILE"

    def test_read_missing_file_returns_empty_dict(self, tmp_path: Path) -> None:
        adapter = StorageAdapter(tmp_path)
        assert adapter.read("missing.json") == {}

    def test_write_then_read_roundtrip(self, tmp_path: Path) -> None:
        adapter = StorageAdapter(tmp_path)
        payload = {"station": "backlink", "listeners": 3}
        adapter.write("state.json", payload)

        assert (tmp_path / "state.json").is_file()
        assert adapter.read("state.json") == payload

    def test_write_is_valid_json_on_disk(self, tmp_path: Path) -> None:
        adapter = StorageAdapter(tmp_path)
        adapter.write("intel.json", {"trends": ["lofi"]})
        on_disk = json.loads((tmp_path / "intel.json").read_text(encoding="utf-8"))
        assert on_disk == {"trends": ["lofi"]}

    def test_corrupt_json_returns_empty_dict(self, tmp_path: Path) -> None:
        bad = tmp_path / "broken.json"
        bad.write_text("{not-json", encoding="utf-8")
        adapter = StorageAdapter(tmp_path)
        assert adapter.read("broken.json") == {}

    def test_path_traversal_on_read_raises(self, tmp_path: Path) -> None:
        adapter = StorageAdapter(tmp_path)
        with pytest.raises(ValueError, match="Path traversal"):
            adapter.read("../escape.json")

    def test_path_traversal_on_write_raises(self, tmp_path: Path) -> None:
        adapter = StorageAdapter(tmp_path)
        with pytest.raises(ValueError, match="Path traversal"):
            adapter.write("../../escape.json", {"nope": True})


@pytest.mark.unit
class TestStorageAdapterFirestoreFallback:
    """Firestore init failures fall back to FILE without network."""

    def test_firestore_type_without_library_falls_back(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("STORAGE_TYPE", "FIRESTORE")
        with patch("hive.utils.storage_adapter.firestore", None):
            adapter = StorageAdapter(tmp_path)
        assert adapter.storage_type == "FILE"
        assert adapter.firestore_client is None

    def test_firestore_client_init_failure_falls_back(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("STORAGE_TYPE", "FIRESTORE")
        monkeypatch.setenv("GCP_PROJECT_ID", "fake-project")
        mock_fs = MagicMock()
        mock_fs.Client.side_effect = RuntimeError("no credentials")
        with patch("hive.utils.storage_adapter.firestore", mock_fs):
            adapter = StorageAdapter(tmp_path)
        assert adapter.storage_type == "FILE"
        adapter.write("state.json", {"ok": True})
        assert adapter.read("state.json") == {"ok": True}

    def test_firestore_read_write_via_mocked_client(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("STORAGE_TYPE", "FIRESTORE")
        monkeypatch.setenv("GCP_PROJECT_ID", "fake-project")

        store: dict[str, dict] = {}

        mock_doc = MagicMock()

        def _get() -> MagicMock:
            snap = MagicMock()
            snap.exists = "state" in store
            snap.to_dict.return_value = store.get("state", {})
            return snap

        mock_doc.get.side_effect = _get
        mock_doc.set.side_effect = lambda data: store.__setitem__("state", data)

        mock_collection = MagicMock()
        mock_collection.document.return_value = mock_doc

        mock_client = MagicMock()
        mock_client.collection.return_value = mock_collection

        mock_fs = MagicMock()
        mock_fs.Client.return_value = mock_client

        with patch("hive.utils.storage_adapter.firestore", mock_fs):
            adapter = StorageAdapter(tmp_path)

        assert adapter.storage_type == "FIRESTORE"
        adapter.write("state.json", {"channel": "on-air"})
        assert adapter.read("state.json") == {"channel": "on-air"}
        mock_client.collection.assert_called_with("hive_data")
        mock_collection.document.assert_called_with("state")
