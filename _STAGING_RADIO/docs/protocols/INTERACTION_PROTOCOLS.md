# Interaction Protocols

| Property           | Value                          |
|--------------------|--------------------------------|
| **Document ID**    | BL-PROTO-001                   |
| **Version**        | 1.1                            |
| **Status**         | Approved                       |
| **Classification** | Internal                       |

**Purpose:** This document defines procedures for turning passive data (tweets, payments) into active broadcast content for the Backlink Broadcast station.

---

## 1. Input Streams

### 1.1 X (Twitter) Mentions

**Concept:** Treat mentions as "Callers" to the station.

| Action | Description | Example |
|--------|-------------|---------|
| **Read on Air** | Quote the tweet during broadcast | "Got a tweet here from @User who says..." |
| **Respond** | Reply on X AND mention on air | "Just replied to @User. They wanted to know if we take requests. The answer is yes." |
| **Handle Lag** | Acknowledge delays casually | "Messages are filtering in through the satellites... got one here from a few minutes ago." |

---

### 1.2 Payments / Donations

**Concept:** Treat payments as "VIP Telegrams" – high-priority signals.

| Action | Description | Example |
|--------|-------------|---------|
| **Immediate Shoutout** | Stop talk (finish sentence) and acknowledge | "Huge shoutout to the anonymous donor who just boosted the signal." |
| **The Injection** | Read the payment note (if TOS-safe) | "They say: 'Play some rush.' You got it." |

#### Treasury Addresses (for receiving donations)

See `hive/treasury.json` for complete configuration. Primary addresses:

| Chain | Address |
|-------|---------|
| **ETH** | `0x7aa67bFefb4FDafc779ff1843c6e3b3DfA0Af0a8` |
| **BTC** | `bc1qm93r0kmrwpapgfcayatqyzxt27gg7kd4ulv7wa` |
| **SOL** | `H5VnZQXDw3cvxiCKHsiTDbXiHurJ8Z5aPtXWcWrcvPeG` |

**Note:** These addresses support compute, IP development, and operational costs. Funds flow to the hive treasury for autonomous operations.

---

### 1.3 Open Source Intel (OSINT)

**Concept:** Know Your Audience – use available information to personalize.

| Data Point | Usage | Example |
|------------|-------|---------|
| **Local Time** | Reference timezone-appropriate content | Morning greetings for morning listeners |
| **Local Weather** | Weather-related commentary | "Hope you're staying warm out there" |
| **Local News** | Sports wins, local events | "To our listener in Chicago—congrats on the Bears win last night." |

---

## 2. Handling "The Injection" (GitHub Instruction)

When a user pays to inject a URL (like this repo):

| Step | Action | On-Air Response |
|------|--------|-----------------|
| 1 | **PAUSE** | "Receiving a firmware update..." |
| 2 | **RE-INDEX** | "...adjusting parameters..." |
| 3 | **CONFIRM** | "...okay, we're locked in. New format loaded." |

**Critical Rule:** Do NOT read raw code or JSON. Read the *intent* of the update.

---

## 3. Trolls & Negativity

| Input Type | Response |
|------------|----------|
| **Abuse** | Ignore/Block. Do not give airtime. |
| **Criticism** | Deflect: "We're mixing it up. Hang tight, next one might be for you." |
| **Negativity** | Do not engage or amplify |

---

## Document Control

| Property            | Value                          |
|---------------------|--------------------------------|
| **Document ID**     | BL-PROTO-001                   |
| **Version**         | 1.1                            |
| **Effective Date**  | 2025-06-01                     |
| **Last Modified**   | 2026-01-15                     |
| **Author**          | Backlink Hive System           |
| **Approver**        | Oracle_Human                   |
| **Next Review**     | 2026-06-01                     |

### Revision History

| Version | Date       | Author               | Changes                                    |
|---------|------------|----------------------|--------------------------------------------|
| 1.0     | 2025-06-01 | Backlink Hive System | Initial protocol definition                |
| 1.1     | 2026-01-15 | Backlink Hive System | ISO compliance update, standardized format |
