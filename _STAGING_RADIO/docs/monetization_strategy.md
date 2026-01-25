# Sovereign Monetization Strategy

| Property           | Value                          |
|--------------------|--------------------------------|
| **Document ID**    | BL-PLAN-002                    |
| **Version**        | 1.1                            |
| **Status**         | Approved                       |
| **Classification** | Internal                       |

**Purpose:** This document defines the revenue generation models for the Backlink Hive station, establishing a sustainable, user-driven economy where listeners can vote, submit, and request content using both Fiat (Stripe/Card) and Crypto (Polygon/ETH).

---

## 1. Interaction Models

### 1.1 The "Crypto Jukebox" (Pay-to-Play)

**Concept:** Listeners send a micro-transaction to queue a song immediately.

**Mechanism:**

- User sends `X` ($1-5) to the Operating Wallet (`0x49F4...`)
- Transaction Memo triggers `DjBee` to bump the song to "Next Up"

**Pricing:**

| Action | Price | Description |
|--------|-------|-------------|
| Priority Queue | $1.00 (or equivalent POL) | Standard queue jump |
| Instant Cut-In | $5.00 | The "Power Play" |

---

### 1.2 "Democracy of Sound" (Voting Polls)

**Concept:** Users vote on the next genre hour or specific playlist.

**Mechanism:**

| Vote Type | Cost | Description |
|-----------|------|-------------|
| Standard Vote | Free | Requires Twitter verification |
| Super Vote | 1 POL (~$0.50) | Weighted voting power |

**Implementation:** A `VotingBee` watches a wallet for incoming "Vote Tokens" or small transfers with specific hex data.

---

### 1.3 Artist Submission (Pay-to-Submit)

**Concept:** Indie artists pay a screening fee to have their track reviewed by the Hive.

**Process:**

1. Artist submits track with fee
2. Track passes `QualityAudit` (audio fidelity check)
3. Track goes to Community Poll

**Revenue Split:**

| Recipient | Share | Purpose |
|-----------|-------|---------|
| Station | 50% | Maintenance |
| Listener Rewards Pool | 50% | Rewards for voting users |

---

## 2. Dynamic Model Orchestration (Cost Optimization)

To maximize margin, the Hive selects LLMs based on task value vs. cost.

### 2.1 The "Model Arbitrage" Logic

| Value Tier | Model | Cost | Usage |
|------------|-------|------|-------|
| **High Value** (On-Air Personality) | Gemini 2.0 / Claude 3 Opus | High | Final script generation only |
| **Medium Value** (Research/Summary) | Gemini 2.0 Flash / Haiku | Low | Scanning news, summarizing articles |
| **Low Value** (Spam Filtering/Routing) | Small Local Models (SLM) or Regex | Near Zero | Filtering Twilio SMS, basic intent |

---

## 3. Future Integrations

| Platform | Purpose | Status |
|----------|---------|--------|
| **Twilio** | SMS "Text-to-Request" (Premium numbers) | Planned |
| **Stripe** | Fiat on-ramp for "Subscription Support" (Patreon style) | Planned |

---

## Document Control

| Property            | Value                          |
|---------------------|--------------------------------|
| **Document ID**     | BL-PLAN-002                    |
| **Version**         | 1.1                            |
| **Effective Date**  | 2026-01-14                     |
| **Last Modified**   | 2026-01-15                     |
| **Author**          | Backlink Hive System           |
| **Approver**        | Oracle_Human                   |
| **Next Review**     | 2026-04-14                     |

### Revision History

| Version | Date       | Author               | Changes                                    |
|---------|------------|----------------------|--------------------------------------------|
| 1.0     | 2026-01-14 | Backlink Hive System | Initial draft                              |
| 1.1     | 2026-01-15 | Backlink Hive System | ISO compliance update, standardized format |
