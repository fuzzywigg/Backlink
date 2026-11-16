"""Unit tests for LIVE hive.bees.content.ontology_manager.OntologyManager.

Covers time-of-day ontology rotation, persona prompt assembly, fallback
adapt_message formatting, and DSPy init gating — no network, Gemini, or
real DSPy LM calls.
"""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from hive.bees.content import ontology_manager as om
from hive.bees.content.ontology_manager import OntologyManager


@pytest.fixture
def manager() -> OntologyManager:
    """Fresh manager with DSPy path forced off (no API / no predictor)."""
    with patch.object(om, "DSPY_AVAILABLE", False):
        return OntologyManager(llm_client=None)


@pytest.mark.unit
class TestRotateOntology:
    """rotate_ontology() hour-band selection."""

    @pytest.mark.parametrize(
        ("hour", "expected"),
        [
            (0, "late_night_lofi"),
            (3, "late_night_lofi"),
            (4, "late_night_lofi"),
            (5, "high_energy_morning"),
            (10, "high_energy_morning"),
            (11, "standard_broadcast"),
            (15, "standard_broadcast"),
            (19, "standard_broadcast"),
            (20, "cyber_sovereign"),
            (23, "cyber_sovereign"),
        ],
    )
    def test_hour_bands(self, manager: OntologyManager, hour: int, expected: str) -> None:
        result = manager.rotate_ontology(timestamp=datetime(2026, 9, 27, hour, 0, 0))
        assert result == expected
        assert manager.current_ontology == expected

    def test_uses_datetime_now_when_timestamp_omitted(self, manager: OntologyManager) -> None:
        fixed = datetime(2026, 9, 27, 2, 30, 0)
        with patch("hive.bees.content.ontology_manager.datetime") as mock_dt:
            mock_dt.now.return_value = fixed
            result = manager.rotate_ontology()
        assert result == "late_night_lofi"


@pytest.mark.unit
class TestGetCurrentOntology:
    """get_current_ontology() returns the active vibe dict."""

    def test_default_is_standard_broadcast(self, manager: OntologyManager) -> None:
        vibe = manager.get_current_ontology()
        assert vibe is not None
        assert "Professional" in vibe["desc"]
        assert "vibes" in vibe["forbidden"]
        assert vibe["pacing"] == "medium"

    def test_reflects_rotated_ontology(self, manager: OntologyManager) -> None:
        manager.rotate_ontology(timestamp=datetime(2026, 9, 27, 21, 0, 0))
        vibe = manager.get_current_ontology()
        assert vibe is not None
        assert vibe["pacing"] == "fast"
        assert "mainstream" in vibe["forbidden"]


@pytest.mark.unit
class TestGetPersonaPrompt:
    """get_persona_prompt() system instruction assembly."""

    def test_includes_persona_name_desc_and_forbidden(self, manager: OntologyManager) -> None:
        manager.current_ontology = "late_night_lofi"
        prompt = manager.get_persona_prompt()
        assert "LATE NIGHT LOFI" in prompt
        assert "Bob Ross meets Cyberpunk" in prompt
        assert "PACING: slow" in prompt
        assert "HYPE" in prompt
        assert "VARY YOUR SENTENCE STRUCTURE" in prompt


@pytest.mark.unit
class TestAdaptMessage:
    """adapt_message() DSPy path and formatted fallback."""

    def test_fallback_wraps_message_with_persona(self, manager: OntologyManager) -> None:
        manager.current_ontology = "cyber_sovereign"
        manager.dspy_initialized = False
        out = manager.adapt_message("Track coming up next.")
        assert "[Persona: cyber_sovereign]" in out
        assert "Track coming up next." in out
        assert "Glitchy, tech-focused" in out

    def test_unknown_ontology_falls_back_to_standard_desc(self, manager: OntologyManager) -> None:
        manager.current_ontology = "not_a_real_vibe"
        manager.dspy_initialized = False
        out = manager.adapt_message("Hello airwaves")
        assert "Hello airwaves" in out
        assert "Professional, clear" in out

    def test_uses_predictor_when_dspy_initialized(self, manager: OntologyManager) -> None:
        manager.dspy_initialized = True
        manager.predictor = MagicMock(
            return_value=SimpleNamespace(adapted_script="Rewritten banter")
        )
        out = manager.adapt_message("Plain facts")
        assert out == "Rewritten banter"
        manager.predictor.assert_called_once()
        kwargs = manager.predictor.call_args.kwargs
        assert kwargs["core_message"] == "Plain facts"
        assert "Professional, clear" in kwargs["persona_desc"]
        assert "Do not use:" in kwargs["constraints"]
        assert "vibes" in kwargs["constraints"]

    def test_predictor_failure_falls_back(
        self, manager: OntologyManager, capsys: pytest.CaptureFixture[str]
    ) -> None:
        manager.dspy_initialized = True
        manager.predictor = MagicMock(side_effect=RuntimeError("lm down"))
        out = manager.adapt_message("Still ship it")
        assert "[Persona: standard_broadcast]" in out
        assert "Still ship it" in out
        assert "DSPy adaptation failed" in capsys.readouterr().out


@pytest.mark.unit
class TestInitDspyGating:
    """__init__ only enables DSPy when available, client set, and key present."""

    def test_no_llm_client_skips_dspy(self) -> None:
        with patch.object(om, "DSPY_AVAILABLE", True):
            mgr = OntologyManager(llm_client=None)
        assert mgr.dspy_initialized is False
        assert mgr.current_ontology == "standard_broadcast"

    def test_missing_gemini_key_skips_dspy(self) -> None:
        # Ensure GEMINI_API_KEY is absent even if autouse fixture set others.
        with (
            patch.object(om, "DSPY_AVAILABLE", True),
            patch("hive.bees.content.ontology_manager.os.getenv", return_value=None),
        ):
            mgr = OntologyManager(llm_client=object())
        assert mgr.dspy_initialized is False

    def test_successful_dspy_init_sets_predictor(self) -> None:
        fake_google = MagicMock(name="GoogleLM")
        fake_predict = MagicMock(name="Predict")
        fake_dspy = MagicMock()
        fake_dspy.Google.return_value = fake_google
        fake_dspy.Predict.return_value = fake_predict

        with (
            patch.object(om, "DSPY_AVAILABLE", True),
            patch.object(om, "dspy", fake_dspy),
            patch.object(om, "PersonaAdapter", object()),
            patch(
                "hive.bees.content.ontology_manager.os.getenv",
                return_value="test-gemini-key",
            ),
        ):
            mgr = OntologyManager(llm_client=object())

        assert mgr.dspy_initialized is True
        assert mgr.predictor is fake_predict
        fake_dspy.Google.assert_called_once_with(
            model="models/gemini-pro", api_key="test-gemini-key"
        )
        fake_dspy.settings.configure.assert_called_once_with(lm=fake_google)

    def test_dspy_init_exception_stays_uninitialized(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        fake_dspy = MagicMock()
        fake_dspy.Google.side_effect = RuntimeError("no provider")

        with (
            patch.object(om, "DSPY_AVAILABLE", True),
            patch.object(om, "dspy", fake_dspy),
            patch(
                "hive.bees.content.ontology_manager.os.getenv",
                return_value="test-gemini-key",
            ),
        ):
            mgr = OntologyManager(llm_client=object())

        assert mgr.dspy_initialized is False
        assert "Failed to init DSPy" in capsys.readouterr().out
