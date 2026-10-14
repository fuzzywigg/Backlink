"""Unit tests for LIVE hive.utils.payment_gate.PaymentGate.

Uses temp honeycomb fixtures and mocked analytics/Discord —
no network or real webhooks.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from hive.utils.payment_gate import PaymentGate


@pytest.fixture
def honeycomb(tmp_path: Path) -> Path:
    """Minimal honeycomb directory for PaymentGate file ops."""
    hive = tmp_path / "hive"
    honeycomb = hive / "honeycomb"
    honeycomb.mkdir(parents=True)
    (honeycomb / "intel.json").write_text(
        json.dumps(
            {"listeners": {"known_nodes": {"alice": {"handle": "alice", "wallet_balance": 1.0}}}}
        ),
        encoding="utf-8",
    )
    (honeycomb / "nodes.json").write_text(
        json.dumps({"nodes": {"node-1": {"stake": 100.0}}}),
        encoding="utf-8",
    )
    (honeycomb / "state.json").write_text(
        json.dumps({"settings": {"verbose_logging": False}}),
        encoding="utf-8",
    )
    return hive


@pytest.mark.unit
class TestPaymentGateRefund:
    """PaymentGate.process_refund() credit + incident log."""

    @patch("hive.utils.payment_gate.analytics")
    def test_refund_credits_balance_and_logs(
        self, mock_analytics: MagicMock, honeycomb: Path
    ) -> None:
        gate = PaymentGate(hive_path=honeycomb)
        result = gate.process_refund("alice", 5.0, "song_not_found", node_id="node-1")

        assert result["status"] == "refunded"
        assert result["amount"] == 5.0
        assert result["recipient"] == "alice"

        intel = json.loads((honeycomb / "honeycomb" / "intel.json").read_text(encoding="utf-8"))
        assert intel["listeners"]["known_nodes"]["alice"]["wallet_balance"] == 6.0

        log_path = honeycomb / "honeycomb" / "incident_log.jsonl"
        assert log_path.exists()
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["type"] == "refund"
        assert entry["user"] == "alice"

        mock_analytics.track_event.assert_called_once()

    @patch("hive.utils.payment_gate.analytics")
    def test_refund_creates_listener_if_missing(
        self, mock_analytics: MagicMock, honeycomb: Path
    ) -> None:
        gate = PaymentGate(hive_path=honeycomb)
        gate.process_refund("newbie", 2.5, "timeout")
        intel = json.loads((honeycomb / "honeycomb" / "intel.json").read_text(encoding="utf-8"))
        assert intel["listeners"]["known_nodes"]["newbie"]["wallet_balance"] == 2.5
        mock_analytics.track_event.assert_called_once()


@pytest.mark.unit
class TestPaymentGateSlash:
    """PaymentGate.slash_node() stake reduction."""

    @patch("hive.utils.payment_gate.analytics")
    def test_slash_reduces_stake(self, mock_analytics: MagicMock, honeycomb: Path) -> None:
        gate = PaymentGate(hive_path=honeycomb)
        result = gate.slash_node("node-1", percentage=0.1)

        assert result["status"] == "slashed"
        assert result["amount_slashed"] == 10.0
        assert result["remaining_stake"] == 90.0

        nodes = json.loads((honeycomb / "honeycomb" / "nodes.json").read_text(encoding="utf-8"))
        assert nodes["nodes"]["node-1"]["stake"] == 90.0
        mock_analytics.track_event.assert_called_once()

    def test_slash_missing_registry(self, tmp_path: Path) -> None:
        hive = tmp_path / "hive"
        (hive / "honeycomb").mkdir(parents=True)
        gate = PaymentGate(hive_path=hive)
        assert gate.slash_node("node-1") == {"error": "Nodes registry not found"}

    @patch("hive.utils.payment_gate.analytics")
    def test_slash_unknown_node(self, _mock_analytics: MagicMock, honeycomb: Path) -> None:
        gate = PaymentGate(hive_path=honeycomb)
        assert gate.slash_node("missing") == {"error": "Node missing not found"}


@pytest.mark.unit
class TestPaymentGateVerbose:
    """PaymentGate._is_verbose_logging() state flag."""

    def test_verbose_false_by_default(self, honeycomb: Path) -> None:
        gate = PaymentGate(hive_path=honeycomb)
        assert gate._is_verbose_logging() is False

    def test_verbose_true_when_enabled(self, honeycomb: Path) -> None:
        state_path = honeycomb / "honeycomb" / "state.json"
        state_path.write_text(json.dumps({"settings": {"verbose_logging": True}}), encoding="utf-8")
        gate = PaymentGate(hive_path=honeycomb)
        assert gate._is_verbose_logging() is True

    def test_verbose_false_when_state_missing(self, tmp_path: Path) -> None:
        hive = tmp_path / "hive"
        (hive / "honeycomb").mkdir(parents=True)
        gate = PaymentGate(hive_path=hive)
        assert gate._is_verbose_logging() is False
