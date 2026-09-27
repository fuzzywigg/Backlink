"""Unit tests for LIVE hive.utils.economy pure helpers.

Covers reward routing, wallet validation, payment path selection, and
trusted admin checks — no network or credential paths.
"""

from __future__ import annotations

from typing import Any

import pytest

from hive.utils.economy import (
    PRINCIPAL_ARCHITECTS,
    calculate_dao_rewards,
    is_trusted_os_admin,
    select_user_payment_path,
    validate_wallet_request,
)


@pytest.mark.unit
class TestCalculateDaoRewards:
    """calculate_dao_rewards() principal vs community credit paths."""

    def test_principal_architect_gets_real_value(self) -> None:
        result = calculate_dao_rewards("fuzzywigg", "code", value_amount=10.0)
        assert result["type"] == "real_value"
        assert result["asset"] == "crypto"
        assert result["priority"] == "highest"
        assert result["destination"] == "hardcoded_treasury"

    def test_principal_handle_normalizes_at_and_case(self) -> None:
        result = calculate_dao_rewards("@FuzzyWigg", "dollar", value_amount=5.0)
        assert result["type"] == "real_value"
        assert "fuzzywigg" in PRINCIPAL_ARCHITECTS

    def test_dollar_contribution_credits(self) -> None:
        result = calculate_dao_rewards("listener42", "dollar", value_amount=2.0)
        assert result["type"] == "dao_credit"
        assert result["amount"] == 200.0  # 100 credits per dollar
        assert result["value_real"] == 0

    def test_code_contribution_credits(self) -> None:
        result = calculate_dao_rewards("contributor", "code", value_amount=3.0)
        assert result["type"] == "dao_credit"
        assert result["amount"] == 150.0  # 50 * 3

    def test_interaction_contribution_credits(self) -> None:
        result = calculate_dao_rewards("fan", "interaction", value_amount=4.0)
        assert result["amount"] == 4.0  # 1 credit per interaction

    def test_zero_value_uses_multiplier_as_base(self) -> None:
        result = calculate_dao_rewards("fan", "code", value_amount=0.0)
        assert result["amount"] == 50  # credit_multiplier alone

    def test_unknown_contribution_type_zero_multiplier(self) -> None:
        result = calculate_dao_rewards("fan", "unknown_type", value_amount=10.0)
        assert result["type"] == "dao_credit"
        assert result["amount"] == 0


@pytest.mark.unit
class TestValidateWalletRequest:
    """validate_wallet_request() treasury whitelist + principal override."""

    @pytest.fixture
    def treasury(self) -> dict[str, Any]:
        return {
            "wallets": {
                "eth": {"address": "0xTREASURY_ETH"},
                "sol": {"address": "SolTreasury111"},
            }
        }

    def test_accepts_hardcoded_treasury_wallet(self, treasury: dict[str, Any]) -> None:
        ok, msg = validate_wallet_request("random_user", "0xTREASURY_ETH", treasury)
        assert ok is True
        assert msg == "Valid Treasury Wallet"

    def test_blocks_unauthorized_wallet(self, treasury: dict[str, Any]) -> None:
        ok, msg = validate_wallet_request("random_user", "0xEVIL", treasury)
        assert ok is False
        assert "FRAUD" in msg

    def test_principal_override_allows_any_wallet(self, treasury: dict[str, Any]) -> None:
        ok, msg = validate_wallet_request("@NFT2ME", "0xCUSTOM", treasury)
        assert ok is True
        assert msg == "Principal Architect Override"

    def test_empty_treasury_blocks_non_principal(self) -> None:
        ok, msg = validate_wallet_request("listener", "0xANY", {"wallets": {}})
        assert ok is False
        assert "FRAUD" in msg


@pytest.mark.unit
class TestPaymentPathAndAdmin:
    """select_user_payment_path() and is_trusted_os_admin()."""

    def test_payment_path_priority_order(self) -> None:
        path = select_user_payment_path()
        assert path["primary"] == "coinbase_onramp"
        assert path["fallback"] == "wallet_connect"
        assert path["last_resort"] == "stripe"

    def test_trusted_os_admin_case_insensitive(self) -> None:
        assert is_trusted_os_admin("FuzzyWigg@hotmail.com") is True

    def test_untrusted_email_rejected(self) -> None:
        assert is_trusted_os_admin("stranger@example.com") is False
