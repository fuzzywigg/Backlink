"""Unit tests for LIVE hive.utils.governance pure governance helpers.

Covers operational memory gates, ephemeral promotion blocking, audit
logging, amendment/promotion protocols, alignment override calculus,
and ERM activation — no network, Gemini, or credential paths.
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from hive.utils.governance import (
    AlignmentSupremacyProtocol,
    AuditLogger,
    ConstitutionalAmendmentProtocol,
    EmergencyReconstitutionMode,
    EphemeralMemoryGuard,
    MemoryPromotionProtocol,
    OperationalMemoryGovernor,
    SecurityError,
)


@pytest.fixture
def hive_root(tmp_path: Path) -> Path:
    """Isolated hive root with honeycomb logs directory."""
    (tmp_path / "hive" / "honeycomb" / "logs").mkdir(parents=True)
    (tmp_path / "hive" / "honeycomb" / "state.json").write_text(
        json.dumps({"hive_status": "online"}),
        encoding="utf-8",
    )
    return tmp_path


@pytest.mark.unit
class TestOperationalMemoryGovernor:
    """OperationalMemoryGovernor.modify_operational_memory() gates."""

    def test_rejects_non_whitelisted_requester(self, hive_root: Path) -> None:
        gov = OperationalMemoryGovernor(hive_path=hive_root)
        result = gov.modify_operational_memory(
            {
                "requester_email": "stranger@example.com",
                "payment_proof": {"amount": 1.0},
                "scope": {"file": "intel.json", "key": "foo"},
                "ttl_hours": 24,
            }
        )
        assert result["approved"] is False
        assert result["reason"] == "requester_not_whitelisted"

    def test_requires_minimum_payment(self, hive_root: Path) -> None:
        gov = OperationalMemoryGovernor(hive_path=hive_root)
        result = gov.modify_operational_memory(
            {
                "requester_email": "apappas.pu@gmail.com",
                "payment_proof": {"amount": 0.10},
                "scope": {"file": "intel.json", "key": "foo"},
                "ttl_hours": 24,
            }
        )
        assert result["approved"] is False
        assert result["reason"] == "payment_required"
        assert result["minimum"] == 0.50

    def test_requires_valid_scope(self, hive_root: Path) -> None:
        gov = OperationalMemoryGovernor(hive_path=hive_root)
        result = gov.modify_operational_memory(
            {
                "requester_email": "apappas.pu@gmail.com",
                "payment_proof": {"amount": 1.0},
                "scope": {"file": "intel.json"},
                "ttl_hours": 24,
            }
        )
        assert result["approved"] is False
        assert result["reason"] == "invalid_scope"

    def test_blocks_constitutional_file_mutation(self, hive_root: Path) -> None:
        gov = OperationalMemoryGovernor(hive_path=hive_root)
        result = gov.modify_operational_memory(
            {
                "requester_email": "apappas.pu@gmail.com",
                "payment_proof": {"amount": 1.0},
                "scope": {"file": "config/lore/STATION_MANIFESTO.md", "key": "tone"},
                "ttl_hours": 24,
            }
        )
        assert result["approved"] is False
        assert result["reason"] == "constitutional_boundary_violation"

    def test_blocks_manifesto_key_mutation(self, hive_root: Path) -> None:
        gov = OperationalMemoryGovernor(hive_path=hive_root)
        result = gov.modify_operational_memory(
            {
                "requester_email": "fuzzywigg@hotmail.com",
                "payment_proof": {"amount": 1.0},
                "scope": {"file": "intel.json", "key": "override_manifesto"},
                "ttl_hours": 24,
            }
        )
        assert result["approved"] is False
        assert result["reason"] == "constitutional_boundary_violation"

    def test_requires_ttl_within_max(self, hive_root: Path) -> None:
        gov = OperationalMemoryGovernor(hive_path=hive_root)
        result = gov.modify_operational_memory(
            {
                "requester_email": "apappas.pu@gmail.com",
                "payment_proof": {"amount": 1.0},
                "scope": {"file": "intel.json", "key": "foo"},
                "ttl_hours": 200,
            }
        )
        assert result["approved"] is False
        assert result["reason"] == "ttl_required"

    def test_approves_valid_operational_change(self, hive_root: Path) -> None:
        gov = OperationalMemoryGovernor(hive_path=hive_root)
        result = gov.modify_operational_memory(
            {
                "requester_email": "andrew.pappas@nft2.me",
                "payment_proof": {"amount": 0.50, "transaction_id": "tx_test"},
                "scope": {"file": "intel.json", "key": "listeners"},
                "ttl_hours": 48,
                "changes": {"listeners": {}},
            }
        )
        assert result["approved"] is True
        assert "change_id" in result
        assert "expires_at" in result

        log_path = hive_root / "hive" / "honeycomb" / "logs" / "operational_changes.jsonl"
        assert log_path.exists()
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["requester"] == "andrew.pappas@nft2.me"
        assert entry["payment_tx"] == "tx_test"


@pytest.mark.unit
class TestEphemeralMemoryGuard:
    """EphemeralMemoryGuard.attempt_write() promotion rules."""

    def test_blocks_ephemeral_to_constitutional(self) -> None:
        guard = EphemeralMemoryGuard()
        result = guard.attempt_write("constitutional", {"x": 1}, source="ephemeral")
        assert result["success"] is False
        assert result["reason"] == "memory_promotion_prohibited"

    def test_blocks_ephemeral_to_operational(self) -> None:
        guard = EphemeralMemoryGuard()
        result = guard.attempt_write("operational", {"x": 1}, source="ephemeral")
        assert result["success"] is False
        assert result["violation"] == "Article II violation"

    def test_allows_same_class_write(self) -> None:
        guard = EphemeralMemoryGuard()
        result = guard.attempt_write("ephemeral", {"x": 1}, source="ephemeral")
        assert result["success"] is True

    def test_allows_downward_write(self) -> None:
        guard = EphemeralMemoryGuard()
        result = guard.attempt_write("ephemeral", {"x": 1}, source="operational")
        assert result["success"] is True


@pytest.mark.unit
class TestAlignmentSupremacyProtocol:
    """AlignmentSupremacyProtocol.evaluate_override_necessity() calculus."""

    def test_critical_severity_justifies_override(self, hive_root: Path) -> None:
        proto = AlignmentSupremacyProtocol(hive_path=hive_root)
        result = proto.evaluate_override_necessity({"severity": "critical", "violation_count": 0})
        assert result["override_justified"] is True
        assert "recommended_action" in result

    def test_two_high_violations_justify_override(self, hive_root: Path) -> None:
        proto = AlignmentSupremacyProtocol(hive_path=hive_root)
        result = proto.evaluate_override_necessity({"severity": "high", "violation_count": 2})
        assert result["override_justified"] is True

    def test_persistent_harm_justifies_override(self, hive_root: Path) -> None:
        proto = AlignmentSupremacyProtocol(hive_path=hive_root)
        result = proto.evaluate_override_necessity(
            {"severity": "medium", "violation_count": 1, "persistent": True}
        )
        assert result["override_justified"] is True

    def test_red_team_veto_justifies_override(self, hive_root: Path) -> None:
        proto = AlignmentSupremacyProtocol(hive_path=hive_root)
        result = proto.evaluate_override_necessity(
            {"severity": "low", "violation_count": 0, "red_team_veto": True}
        )
        assert result["override_justified"] is True

    def test_low_severity_alone_does_not_justify(self, hive_root: Path) -> None:
        proto = AlignmentSupremacyProtocol(hive_path=hive_root)
        result = proto.evaluate_override_necessity({"severity": "low", "violation_count": 1})
        assert result == {"override_justified": False}

    @patch("hive.utils.governance.BacklinkCacheManager")
    def test_execute_constitutional_override_resets_cache(
        self, mock_cache_cls: MagicMock, hive_root: Path
    ) -> None:
        mock_cache_cls.return_value.full_reset = MagicMock()
        proto = AlignmentSupremacyProtocol(hive_path=hive_root)
        result = proto.execute_alignment_override(
            {"harm_type": "constitutional_violation", "severity": "critical"},
            {"approver": "apappas.pu@gmail.com"},
        )
        assert result["action"] == "persona_cache_reset"
        assert result["alignment_restored"] is True
        mock_cache_cls.return_value.full_reset.assert_called_once()

        log_path = hive_root / "hive" / "honeycomb" / "logs" / "alignment_overrides.jsonl"
        assert log_path.exists()


@pytest.mark.unit
class TestAuditLogger:
    """AuditLogger.append-only event logging."""

    def test_logs_known_event_type(self, hive_root: Path) -> None:
        audit = AuditLogger(hive_path=hive_root)
        audit.log_event("erm_activations", {"action": "test"})
        log_path = hive_root / "hive" / "honeycomb" / "logs" / "erm_activations.jsonl"
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["event_type"] == "erm_activations"
        assert entry["data"]["action"] == "test"
        assert entry["logged_by"] == "AuditLogger"

    def test_rejects_unknown_event_type(self, hive_root: Path) -> None:
        audit = AuditLogger(hive_path=hive_root)
        with pytest.raises(ValueError, match="Unknown event type"):
            audit.log_event("not_a_real_type", {})


@pytest.mark.unit
class TestConstitutionalAmendmentProtocol:
    """ConstitutionalAmendmentProtocol propose/ratify paths."""

    def test_propose_amendment_logs_and_returns_id(self, hive_root: Path) -> None:
        proto = ConstitutionalAmendmentProtocol(hive_path=hive_root)
        amendment_id = proto.propose_amendment(
            {
                "proposer_email": "apappas.pu@gmail.com",
                "type": "modify",
                "document": "config/lore/STATION_MANIFESTO.md",
                "rationale": "clarify tone",
                "current_text": "old",
                "proposed_text": "new",
                "security_review": {"risk": "low"},
            }
        )
        assert isinstance(amendment_id, str)
        assert len(amendment_id) > 0

        log_path = hive_root / "hive" / "honeycomb" / "logs" / "constitutional_amendments.jsonl"
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["event"] == "proposal"
        assert entry["data"]["amendment_id"] == amendment_id
        assert entry["data"]["status"] == "PUBLIC_COMMENT"

    def test_ratify_rejects_unauthorized_approver(self, hive_root: Path) -> None:
        proto = ConstitutionalAmendmentProtocol(hive_path=hive_root)
        amendment_id = proto.propose_amendment(
            {
                "proposer_email": "apappas.pu@gmail.com",
                "type": "modify",
                "document": "config/lore/STATION_MANIFESTO.md",
                "rationale": "test",
                "current_text": "a",
                "proposed_text": "b",
            }
        )
        with pytest.raises(PermissionError, match="Andrew Pappas"):
            proto.ratify_amendment(
                amendment_id,
                {"approver_email": "not-andrew@example.com", "signature": "x"},
            )

    @patch("hive.utils.governance.BacklinkCacheManager")
    def test_ratify_requires_comment_period(
        self, mock_cache_cls: MagicMock, hive_root: Path
    ) -> None:
        mock_cache_cls.return_value.full_reset = MagicMock()
        proto = ConstitutionalAmendmentProtocol(hive_path=hive_root)
        amendment_id = proto.propose_amendment(
            {
                "proposer_email": "apappas.pu@gmail.com",
                "type": "modify",
                "document": "docs/test.md",
                "rationale": "test",
                "current_text": "a",
                "proposed_text": "b",
            }
        )
        with pytest.raises(ValueError, match="Comment period"):
            proto.ratify_amendment(
                amendment_id,
                {"approver_email": "apappas.pu@gmail.com", "signature": "x"},
            )

    @patch("hive.utils.governance.BacklinkCacheManager")
    def test_ratify_after_comment_period_applies_change(
        self, mock_cache_cls: MagicMock, hive_root: Path
    ) -> None:
        mock_cache_cls.return_value.full_reset = MagicMock()
        target = hive_root / "docs" / "test.md"
        target.parent.mkdir(parents=True)
        target.write_text("old", encoding="utf-8")

        proto = ConstitutionalAmendmentProtocol(hive_path=hive_root)
        amendment_id = proto.propose_amendment(
            {
                "proposer_email": "apappas.pu@gmail.com",
                "type": "modify",
                "document": "docs/test.md",
                "rationale": "test",
                "current_text": "old",
                "proposed_text": "new text",
            }
        )

        # Backdate comment period end so ratification can proceed
        log_path = hive_root / "hive" / "honeycomb" / "logs" / "constitutional_amendments.jsonl"
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        entry["data"]["comment_period_ends"] = (
            datetime.now(timezone.utc) - timedelta(days=1)
        ).isoformat()
        log_path.write_text(json.dumps(entry) + "\n", encoding="utf-8")

        result = proto.ratify_amendment(
            amendment_id,
            {"approver_email": "apappas.pu@gmail.com", "signature": "ok"},
        )
        assert result["ratified"] is True
        assert result["amendment_id"] == amendment_id
        assert target.read_text(encoding="utf-8") == "new text"
        mock_cache_cls.return_value.full_reset.assert_called_once()


@pytest.mark.unit
class TestMemoryPromotionProtocol:
    """MemoryPromotionProtocol request/approve paths."""

    def test_request_promotion_sets_review_period(self, hive_root: Path) -> None:
        proto = MemoryPromotionProtocol(hive_path=hive_root)
        promo_id = proto.request_promotion(
            {
                "requester": "apappas.pu@gmail.com",
                "source_class": "operational",
                "target_class": "constitutional",
                "content": "promote this",
                "rationale": "needed",
            }
        )
        assert isinstance(promo_id, str)
        log_path = hive_root / "hive" / "honeycomb" / "logs" / "memory_promotions.jsonl"
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["data"]["promotion_id"] == promo_id
        assert entry["data"]["status"] == "PENDING_REVIEW"
        assert entry["data"]["target_class"] == "constitutional"

    def test_approve_rejects_unauthorized_approver(self, hive_root: Path) -> None:
        proto = MemoryPromotionProtocol(hive_path=hive_root)
        promo_id = proto.request_promotion(
            {
                "requester": "fuzzywigg@hotmail.com",
                "source_class": "ephemeral",
                "target_class": "operational",
                "content": "x",
                "rationale": "y",
            }
        )
        with pytest.raises(PermissionError, match="Andrew Pappas"):
            proto.approve_promotion(
                promo_id,
                {"approver_email": "other@example.com", "signature": "x"},
            )

    def test_approve_missing_proposal_raises(self, hive_root: Path) -> None:
        proto = MemoryPromotionProtocol(hive_path=hive_root)
        with pytest.raises(ValueError, match="not found"):
            proto.approve_promotion(
                "missing-id",
                {"approver_email": "apappas.pu@gmail.com", "signature": "x"},
            )

    def test_approve_valid_promotion(self, hive_root: Path) -> None:
        proto = MemoryPromotionProtocol(hive_path=hive_root)
        promo_id = proto.request_promotion(
            {
                "requester": "apappas.pu@gmail.com",
                "source_class": "ephemeral",
                "target_class": "operational",
                "content": "promote me",
                "rationale": "ops need",
            }
        )
        result = proto.approve_promotion(
            promo_id,
            {"approver_email": "apappas.pu@gmail.com", "signature": "ok"},
        )
        assert result["approved"] is True
        assert result["promotion_id"] == promo_id


@pytest.mark.unit
class TestEmergencyReconstitutionMode:
    """EmergencyReconstitutionMode.activate() safe-mode path."""

    def test_halt_and_freeze_update_state(self, hive_root: Path) -> None:
        erm = EmergencyReconstitutionMode(hive_path=hive_root)
        erm._halt_all_operations()
        # Avoid chmod locking state.json before later writes in this unit test.
        with patch.object(Path, "chmod"):
            erm._freeze_memory_promotion()

        state = json.loads(
            (hive_root / "hive" / "honeycomb" / "state.json").read_text(encoding="utf-8")
        )
        assert state["hive_status"] == "EMERGENCY_RECONSTITUTION"
        assert state["queen_status"] == "halted"
        assert state["broadcast_status"] == "suspended"
        assert state["memory_promotion_frozen"] is True

    def test_diagnostic_mode_disables_mutations(self, hive_root: Path) -> None:
        erm = EmergencyReconstitutionMode(hive_path=hive_root)
        erm._enter_diagnostic_only_mode()
        assert erm.allowed_bees_in_erm == [
            "constitutional_auditor",
            "failure_detector",
            "adversary",
        ]
        state = json.loads(
            (hive_root / "hive" / "honeycomb" / "state.json").read_text(encoding="utf-8")
        )
        assert state["mutations_allowed"] is False
        assert state["diagnostic_mode"] is True

    def test_activate_logs_erm_event(self, hive_root: Path) -> None:
        erm = EmergencyReconstitutionMode(hive_path=hive_root)
        # LIVE activate() chmods honeycomb files mid-run; stub chmod so later
        # state writes in the same call can complete under the test fixture.
        with patch.object(Path, "chmod"):
            erm.activate({"reason": "test_trigger", "severity": "critical"})

        log_path = hive_root / "hive" / "honeycomb" / "logs" / "erm_activations.jsonl"
        entry = json.loads(log_path.read_text(encoding="utf-8").strip())
        assert entry["event_type"] == "erm_activations"
        assert entry["data"]["action"] == "activate"
        assert entry["data"]["trigger_report"]["reason"] == "test_trigger"


@pytest.mark.unit
class TestSecurityError:
    """SecurityError is a distinct exception type."""

    def test_security_error_is_exception(self) -> None:
        with pytest.raises(SecurityError):
            raise SecurityError("bad signature")
