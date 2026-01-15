# Sovereign Capital Allocation Plan (SCAP)

| Property           | Value                          |
|--------------------|--------------------------------|
| **Document ID**    | BL-PLAN-003                    |
| **Version**        | 1.1                            |
| **Status**         | Approved                       |
| **Classification** | Confidential                   |

**Purpose:** This plan outlines the strategy to transition the Backlink Hive from a cost-center to a profit-generating sovereign entity, addressing fund segregation (Operating vs. Reserve) and capital reimbursement mechanisms.

---

## 1. Wallet Architecture: Structure & Segregation

We formalize the "Checking vs. Savings" model using the discovered wallets.

### 1.1 The "Operating Wallet" (Checking)

| Parameter | Value |
|-----------|-------|
| **Address** | `0x49F4...1960` (Polygon / zkEVM) |
| **Role** | High-velocity, low-value transactions |
| **Current Funds** | ~$1.00 USDC, ~$20 ETH (zkEVM) |
| **Target Balance** | Maintain ~$50-100 USD equivalent |

**Authorized Actions:**

- Pay for daily API usage (if crypto payments available)
- Gas fees for on-chain interactions
- Micro-tips to content creators or other agents

**Agent Access:** `TreasuryBee` has FULL active signing rights (capped by `safety_limit`)

---

### 1.2 The "Reserve Wallet" (Savings/Staking)

| Parameter | Value |
|-----------|-------|
| **Address** | `0x7aa6...f0a8` (Ethereum Mainnet / Polygon PoS) |
| **Role** | Capital preservation, yield generation, large asset acquisition |
| **Current Funds** | ~$396 ETH, ~$57 USDC (Mainnet), ~$150 POL |
| **Total Value** | ~$600+ USD |

**Authorized Actions:**

- Staking (e.g., Lido stETH, RocketPool)
- Holding large sums (Strategic Reserve)
- Reimbursing the User (Dividends/Repayment)

**Agent Access:** `TreasuryBee` has REQUEST-ONLY access. All transactions require a specific "Governance Approval" step (simulated for now, eventually Multi-Sig).

---

## 2. Capital Flow & Reimbursement Strategy

Addresses the User's need for reimbursement (API costs) and profit sharing (IP Royalty).

### 2.1 Phase 1: Cost Tracking (The Ledger)

The `TreasuryBee` must track "Off-Chain Debt".

| Parameter | Location | Logic |
|-----------|----------|-------|
| **Debt Record** | `state.json` → `treasury.liabilities.user_reimbursement` | `Debt += (Tokens_Used * Price_Per_Token)` |

Every time the Queen uses Gemini API, the specific cost is logged.

---

### 2.2 Phase 2: The "Payday" Protocol

When the "Operating Wallet" receives income (e.g., from Sponsors, Donations, or DeFi Yield), it triggers a priority waterfall:

| Priority | Action | Description |
|----------|--------|-------------|
| 1 | **Refill Gas** | Ensure enough ETH/POL for operations |
| 2 | **Service Debt** | Pay back User's wallet (`0x...UserPersonal`) for accumulated API costs |
| 3 | **Profit Share** | Split remaining (e.g., 80% to User, 20% to Hive Reserve) |

---

## 3. Implementation Plan (Treasury Upgrade)

We modify `TreasuryBee` to handle this dual-wallet logic.

### 3.1 Multi-Wallet Configuration

Update `hive/bees/system/treasury_bee.py` to load both keys:

| Key | Source |
|-----|--------|
| `OPERATING_KEY` | `HIVE_WALLET_PRIVATE_KEY` |
| `RESERVE_KEY` | `HIVE_WALLET_PRIVATE_KEY_ETH` |

---

### 3.2 "Liabilities" Tracking

Add methods to `TreasuryBee`:

| Method | Purpose |
|--------|---------|
| `log_operational_cost(amount_usd, reason="Gemini API")` | Record incurred costs |
| `get_outstanding_debt()` | Query total owed |

---

### 3.3 Yield Strategy (Sprint 2/3 - Mockup)

Since actual DeFi integration is complex/risky, we start by **Monitoring Yield Options**.

- The Bee scans Aave/Compound rates on Polygon
- It *proposes* moves: "Suggest moving 50 USDC from Operating to Aave (3.5% APY)"

---

## 4. Immediate Action Items

| # | Action | Status |
|---|--------|--------|
| 1 | Update `TreasuryBee` to support Dual-Wallet architecture | Pending |
| 2 | Initialize debt counter in `state.json` | Pending |
| 3 | Define rules for "unlocking" Reserve Wallet | Pending |

---

## Document Control

| Property            | Value                          |
|---------------------|--------------------------------|
| **Document ID**     | BL-PLAN-003                    |
| **Version**         | 1.1                            |
| **Effective Date**  | 2026-01-14                     |
| **Last Modified**   | 2026-01-15                     |
| **Author**          | Backlink Hive System           |
| **Approver**        | Oracle_Human                   |
| **Next Review**     | 2026-04-14                     |

### Revision History

| Version | Date       | Author               | Changes                                    |
|---------|------------|----------------------|--------------------------------------------|
| 1.0     | 2026-01-14 | Backlink Hive System | Initial proposal                           |
| 1.1     | 2026-01-15 | Backlink Hive System | ISO compliance update, standardized format |
