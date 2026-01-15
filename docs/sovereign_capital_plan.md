# Sovereign Capital Allocation Plan (SCAP)

## Executive Summary

This plan outlines the strategy to transition the Backlink Hive from a cost-center to a profit-generating sovereign entity. It addresses the User's requirement to segregate funds (Operating vs. Reserve) and establishes a clear mechanism for reimbursing initial capital outlays (e.g., API costs).

## 1. Wallet Architecture: Structure & Segregation

We will formalize the "Checking vs. Savings" model using the discovered wallets.

### A. The "Operating Wallet" (Checking)

**Address**: `0x49F4...1960` (Polygon / zkEVM)

* **Role**: High-velocity, low-value transactions.
* **Funds**:
  * Currently: ~$1.00 USDC, ~$20 ETH (zkEVM).
  * Target: Maintain ~$50-100 USD equivalent.
* **Authorized Actions**:
  * Pay for daily API usage (if crypto payments available).
  * Gas fees for on-chain interactions.
  * Micro-tips to content creators or other agents.
* **Agent Access**: `TreasuryBee` has FULL active signing rights (capped by `safety_limit`).

### B. The "Reserve Wallet" (Savings/Staking)

**Address**: `0x7aa6...f0a8` (Ethereum Mainnet / Polygon PoS)

* **Role**: Capital preservation, yield generation, and large asset acquisition.
* **Funds**:
  * Currently: ~$396 ETH, ~$57 USDC (Mainnet), ~$150 POL.
  * Total: ~$600+ USD.
* **Authorized Actions**:
  * Staking (e.g., Lido stETH, RocketPool).
  * Holding large sums (Strategic Reserve).
  * Reimbursing the User (Dividends/Repayment).
* **Agent Access**: `TreasuryBee` has REQUEST-ONLY access. All transactions require a specific "Governance Approval" step (simulated for now, eventually Multi-Sig).

## 2. Capital Flow & Reimbursement Strategy

To address the User's need for reimbursement (API costs) and profit sharing (IP Royalty).

### Phase 1: Cost Tracking (The Ledger)

The `TreasuryBee` must track "Off-Chain Debt".

* Every time the Queen uses Gemini API, the specific cost is logged.
* **Debt Record**: `state.json` -> `treasury.liabilities.user_reimbursement`.
* **Logic**: `Debt += (Tokens_Used * Price_Per_Token)`.

### Phase 2: The "Payday" Protocol

When the "Operating Wallet" receives income (e.g., from Sponsors, Donations, or DeFi Yield), it triggers a priority waterfall:

1. **Refill Gas**: Ensure enough ETH/POL for operations.
2. **Service Debt**: Pay back the User's registered wallet (`0x...UserPersonal`) for accumulated API costs.
3. **Profit Share**: Split remaining net profit (e.g., 80% to User, 20% to Hive Reserve).

## 3. Implementation Plan (Treasury Upgrade)

We will modify `TreasuryBee` to handle this dual-wallet logic.

### Step 1: Multi-Wallet Configuration

Update `hive/bees/system/treasury_bee.py` to load both keys:
* `OPERATING_KEY`: From `HIVE_WALLET_PRIVATE_KEY`
* `RESERVE_KEY`: From `HIVE_WALLET_PRIVATE_KEY_ETH`

### Step 2: "Liabilities" Tracking

Add methods to `TreasuryBee`:
* `log_operational_cost(amount_usd, reason="Gemini API")`
* `get_outstanding_debt()`

### Step 3: Yield Strategy (Mockup for Sprint 2/3)

Since actual DeFi integration is complex/risky, we will start by **Monitoring Yield Options**.
* The Bee will scan Aave/Compound rates on Polygon.
* It will *propose* moves: "Suggest moving 50 USDC from Operating to Aave (3.5% APY)."

## 4. Immediate Action Items

1. **Update Implementation**: Modify `TreasuryBee` to support the Dual-Wallet architecture.
2. **Debt Ledger**: Initialize the debt counter in `state.json`.
3. **Governance**: Define the rules for "unlocking" the Reserve Wallet (e.g., "Only for transfers > $100 or Debt Repayment").

---
**Status**: 📋 Proposed
**Date**: 2026-01-14
