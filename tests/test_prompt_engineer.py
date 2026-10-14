"""Unit tests for LIVE hive.utils.prompt_engineer helpers.

Covers fluent prompt construction and JSON output parsing —
no LLM or network calls.
"""

from __future__ import annotations

import pytest

from hive.utils.prompt_engineer import PromptEngineer


@pytest.mark.unit
class TestPromptEngineerBuild:
    """PromptEngineer.build_system_prompt() assembly."""

    def test_role_and_goal_anchor(self) -> None:
        pe = PromptEngineer(role="DJ", goal="Entertain listeners")
        prompt = pe.build_system_prompt()
        assert "ROLE: DJ" in prompt
        assert "GOAL: Entertain listeners" in prompt

    def test_fluent_context_and_constraints(self) -> None:
        pe = (
            PromptEngineer("Scout", "Find trends")
            .add_context("City: Andon")
            .add_section("Sources")
            .add_constraint("No speculation")
            .require_evidence()
            .set_output_format('{"trends": []}')
        )
        prompt = pe.build_system_prompt()
        assert "CONTEXT:" in prompt
        assert "- City: Andon" in prompt
        assert "--- SOURCES ---" in prompt
        assert "CONSTRAINTS (MUST FOLLOW):" in prompt
        assert "- No speculation" in prompt
        assert "list your assumptions" in prompt
        assert "VALID JSON object" in prompt
        assert '{"trends": []}' in prompt

    def test_empty_optional_sections_omitted(self) -> None:
        prompt = PromptEngineer("Bee", "Work").build_system_prompt()
        assert "CONTEXT:" not in prompt
        assert "CONSTRAINTS" not in prompt
        assert "REQUIREMENT:" not in prompt
        assert "OUTPUT FORMAT:" not in prompt


@pytest.mark.unit
class TestParseJsonOutput:
    """PromptEngineer.parse_json_output() markdown-tolerant parsing."""

    def test_parses_raw_json(self) -> None:
        result = PromptEngineer.parse_json_output('{"ok": true, "n": 1}')
        assert result == {"ok": True, "n": 1}

    def test_strips_markdown_fence(self) -> None:
        raw = '```json\n{"status": "ready"}\n```'
        result = PromptEngineer.parse_json_output(raw)
        assert result == {"status": "ready"}

    def test_invalid_json_returns_error_envelope(self) -> None:
        raw = "not json at all"
        result = PromptEngineer.parse_json_output(raw)
        assert result["error"] == "json_parse_error"
        assert result["raw_content"] == raw
