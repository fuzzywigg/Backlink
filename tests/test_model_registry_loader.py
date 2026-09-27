"""Unit tests for LIVE core_utils.model_registry_loader.ModelRegistryLoader.

Covers cache validity, fallback registry, get_model, and recommend_model
with fixtures/mocks — no live models.dev network calls.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from core_utils.model_registry_loader import (
    FALLBACK_REGISTRY,
    ModelRegistryLoader,
)


@pytest.mark.unit
class TestModelRegistryCacheAndFallback:
    """Cache hit path and fetch-failure fallback."""

    def test_loads_valid_cache(self, tmp_path: Path) -> None:
        cache = tmp_path / "models_cache.json"
        payload = {
            "google": {
                "models": {
                    "gemini-test": {
                        "id": "gemini-test",
                        "name": "Gemini Test",
                        "context": 1000,
                        "cost": {"input": 1.0, "output": 2.0},
                        "capabilities": ["reasoning"],
                    }
                }
            }
        }
        cache.write_text(json.dumps(payload), encoding="utf-8")

        with patch.object(ModelRegistryLoader, "_is_cache_valid", return_value=True):
            loader = ModelRegistryLoader(cache_path=str(cache))

        assert loader.get_model("gemini-test")["name"] == "Gemini Test"

    def test_fetch_failure_uses_fallback(self, tmp_path: Path) -> None:
        cache = tmp_path / "models_cache.json"
        with patch("core_utils.model_registry_loader.requests.get") as mock_get:
            mock_get.side_effect = RuntimeError("network down")
            loader = ModelRegistryLoader(cache_path=str(cache))

        assert loader.registry == FALLBACK_REGISTRY
        assert loader.get_model("gpt-4o")["id"] == "gpt-4o"

    def test_fetch_success_writes_cache(self, tmp_path: Path) -> None:
        cache = tmp_path / "models_cache.json"
        remote = {"acme": {"models": {"m1": {"id": "m1", "name": "M1"}}}}
        mock_resp = MagicMock()
        mock_resp.raise_for_status.return_value = None
        mock_resp.json.return_value = remote

        with patch("core_utils.model_registry_loader.requests.get", return_value=mock_resp):
            loader = ModelRegistryLoader(cache_path=str(cache))

        assert loader.get_model("m1")["name"] == "M1"
        assert json.loads(cache.read_text(encoding="utf-8")) == remote


@pytest.mark.unit
class TestModelRegistryQueries:
    """get_model() and recommend_model() pure lookups."""

    def test_get_model_unknown_returns_none(self, tmp_path: Path) -> None:
        cache = tmp_path / "models_cache.json"
        with patch.object(
            ModelRegistryLoader, "_fetch_fresh_registry", return_value=FALLBACK_REGISTRY
        ):
            loader = ModelRegistryLoader(cache_path=str(cache))
        assert loader.get_model("does-not-exist") is None

    def test_recommend_model_modes(self, tmp_path: Path) -> None:
        cache = tmp_path / "models_cache.json"
        with patch.object(
            ModelRegistryLoader, "_fetch_fresh_registry", return_value=FALLBACK_REGISTRY
        ):
            loader = ModelRegistryLoader(cache_path=str(cache))
        assert loader.recommend_model("performance") == "claude-3-5-sonnet-latest"
        assert loader.recommend_model("context") == "gemini-1.5-pro"
        assert loader.recommend_model("cost") == "gpt-4o-mini"
        assert loader.recommend_model("unknown-mode") == "gpt-4o"

    def test_is_cache_valid_missing_file(self, tmp_path: Path) -> None:
        cache = tmp_path / "missing.json"
        with patch.object(ModelRegistryLoader, "_fetch_fresh_registry", return_value={}):
            loader = ModelRegistryLoader(cache_path=str(cache))
        assert loader._is_cache_valid() is False
