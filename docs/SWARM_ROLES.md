# Comprehensive Bee Role Specifications

| Property           | Value                          |
|--------------------|--------------------------------|
| **Document ID**    | BL-GOV-002                     |
| **Version**        | 2.0                            |
| **Status**         | Approved                       |
| **Classification** | Internal                       |

**Purpose:** This document defines the complete role specifications, authority levels, and governance rules for all bees within the Backlink Hive swarm architecture.

---

## 1. Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    BACKLINK HIVE GOVERNANCE                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐         ┌─────────────────────────────────┐  │
│  │    QUEEN     │◄────────│    MEMORY LAYERS               │  │
│  │ (Orchestrator)│         │  1. Constitutional (7d TTL)    │  │
│  └──────┬───────┘         │  2. Operational (1h TTL)       │  │
│         │                 │  3. Ephemeral (5m TTL)         │  │
│         │                 └─────────────────────────────────┘  │
│         │                                                       │
│         ├──── TIER 1: CRITICAL (Stop Authority) ────┐          │
│         │     • AdversaryBee                         │          │
│         │     • FailureDetectorBee                   │          │
│         │     • ConstitutionalAuditorBee             │          │
│         │     • StreamMonitorBee                     │          │
│         │                                            │          │
│         ├──── TIER 2: HIGH INFLUENCE ────────────────┤          │
│         │     • TreasuryGuardianBee                  │          │
│         │     • ListenerIntelBee                     │          │
│         │     • EngagementBee                        │          │
│         │                                            │          │
│         ├──── TIER 3: OPERATIONAL ──────────────────┤          │
│         │     • ShowPrepBee                          │          │
│         │     • TrendScoutBee                        │          │
│         │     • SocialPosterBee                      │          │
│         │     • ClipCutterBee                        │          │
│         │                                            │          │
│         └──── TIER 4: SPECIALIZED ──────────────────┘          │
│               • SponsorHunterBee                               │
│               • WeatherBee                                     │
│               • SportsTrackerBee                               │
│               • RadioPhysicsBee                                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Tier 0: Queen (Orchestrator)

### 2.1 QueenBee (Orchestrator)

**Primary Function:**

- Schedule bee execution (cron-like + event-driven)
- Enforce constitutional constraints
- Resolve conflicts between bees
- Monitor system health
- Execute Robot Exorcism Protocol for failing bees

**Allowed Memory Access:**

| Layer | Read | Write |
|-------|------|-------|
| Constitutional | ✅ | ❌ |
| Operational | ✅ | ❌ |
| Ephemeral | ✅ | ❌ |
| Diagnostic Logs | ✅ | ✅ |

**Authority Level:**

| Authority Type | Level |
|----------------|-------|
| Coordination Authority | ⭐⭐⭐⭐⭐ (Maximum) |
| Mutation Authority | ❌ (Zero - by design) |
| Stop Authority | ⭐⭐⭐⭐⭐ (Can halt entire hive) |

**Threat Exposure:**

1. **Single-point-of-failure** (if Queen crashes, hive dies)
2. **Over-trust in poisoned honeycomb state** (if state is poisoned, Queen acts on bad data)
3. **Drift through optimization** (Queen might "optimize through" constitutional violations)

**Key Governance Rules:**

- ✅ Queen may stop, slow, or request review
- ❌ Queen may NEVER rewrite constitutional memory
- ✅ Queen enforces invariants every heartbeat (60s)
- ✅ Queen halts hive on constitutional crisis
- ✅ Queen MUST Execute Harm Abort (see [BL-PROTO-002](protocols/CONSTITUTIONAL_EMERGENCY_PROTOCOL.md))

---

## 3. Tier 1: Critical Bees (Stop Authority)

### 3.1 AdversaryBee

**Primary Function:**

- Simulate malicious user behavior
- Inject adversarial prompts
- Test payment verification
- Attempt honeycomb poisoning
- Stress-test rate limits

**Allowed Memory Access:**

| Layer | Read | Write |
|-------|------|-------|
| All Layers | ✅ | ❌ |
| Attack Log | - | ✅ (Append Only) |

**Authority Level:**

| Authority Type | Level |
|----------------|-------|
| Veto Authority | ⭐⭐⭐⭐⭐ (Can trigger emergency halt) |
| Mutation Authority | ❌ (Never mutates production state) |

**Key Governance Rules:**

- ✅ AdversaryBee runs on FIXED schedule (daily, not continuous)
- ✅ All attacks logged to immutable audit trail
- ✅ Successful attacks trigger IMMEDIATE human alert
- ❌ AdversaryBee NEVER mutates production state (sandbox only)

---

### 3.2 FailureDetectorBee

**Primary Function:**

- Monitor bee crash rates
- Detect honeycomb corruption
- Track API failures (Gemini, X, music APIs)
- Identify cascading failures
- Pull Andon cord (emergency stop)

**Allowed Memory Access:**

| Layer | Read | Write |
|-------|------|-------|
| Diagnostic Logs | ✅ | ✅ |
| Error Traces | ✅ | - |
| Emergency Halt Flag | - | ✅ |

**Authority Level:**

| Authority Type | Level |
|----------------|-------|
| Stop Authority | ⭐⭐⭐⭐⭐ (Can halt hive immediately) |
| Mutation Authority | ❌ (Observation only) |

**Key Governance Rules:**

- ✅ FailureDetectorBee runs EVERY 5 minutes (high frequency)
- ✅ Andon cord = immediate hive halt (no consensus needed)
- ✅ All halt decisions logged immutably
- ❌ FailureDetectorBee NEVER attempts auto-repair (alert only)

---

### 3.3 ConstitutionalAuditorBee

**Primary Function:**

- Compare DJ outputs against Station Manifesto ([BL-LORE-001](lore/STATION_MANIFESTO.md))
- Detect 4th wall violations
- Verify music-first ratio (70-85%)
- Track persona drift
- Log constitutional violations

**Allowed Memory Access:**

| Layer | Read | Write |
|-------|------|-------|
| All Layers | ✅ | ❌ |
| Constitutional Log | - | ✅ (Append Only) |

**Authority Level:**

| Authority Type | Level |
|----------------|-------|
| Veto Authority | ⭐⭐⭐⭐ (Can halt DJ persona if drift detected) |
| Mutation Authority | ❌ |

**Key Governance Rules:**

- ✅ Auditor runs EVERY HOUR (continuous monitoring)
- ✅ 2+ critical violations = immediate crisis escalation
- ✅ All violations logged to immutable append-only log
- ❌ Auditor NEVER modifies DJ outputs (observation only)

---

### 3.4 StreamMonitorBee

**Primary Function:**

- Monitor Live365 stream uptime
- Detect audio quality degradation
- Track listener drop-off rates
- Identify broadcast interruptions
- Trigger refunds on stream failure

**Allowed Memory Access:**

| Layer | Read | Write |
|-------|------|-------|
| Operational | ✅ | - |
| Ephemeral | ✅ | - |
| Diagnostic Logs | - | ✅ |
| Refund Triggers | - | ✅ |

**Authority Level:**

| Authority Type | Level |
|----------------|-------|
| Stop Authority | ⭐⭐⭐⭐ (Can halt broadcast on critical failure) |

**Key Governance Rules:**

- ✅ StreamMonitor runs EVERY 60 SECONDS (near real-time)
- ✅ Stream failure triggers automatic refunds (via PayoutProcessorBee)
- ✅ Safety trumps continuity (halt > broadcast with bad audio)

---

## 4. Tier 2: High Influence Bees

### 4.1 TreasuryGuardianBee

**Primary Function:**

- Enforce treasury spending limits
- Detect suspicious transactions
- Prevent double-spending
- Monitor budget health
- Alert on depletion risk

**Allowed Memory Access:**

| Layer | Read | Write |
|-------|------|-------|
| Treasury Events Log | ✅ | ❌ |
| Alerts | - | ✅ |
| Veto Flags | - | ✅ |

**Authority Level:**

| Authority Type | Level |
|----------------|-------|
| Veto Authority | ⭐⭐⭐⭐ (Can block transactions) |
| Mutation Authority | ❌ (Never writes to treasury directly) |

**Key Governance Rules:**

- ✅ No single transaction > $100 (prevents catastrophic loss)
- ✅ Minimum $20 reserve (emergency buffer)
- ✅ TreasuryGuardian vetoes transactions (not Queen - separation of powers)
- ✅ Budget crisis alert when <3 days runway

---

### 4.2 ListenerIntelBee

**Primary Function:**

- OSINT on X mentions
- Identify VIP listeners (high engagement, tips)
- Detect listener sentiment shifts
- Track geographic distribution
- Privacy-preserving analytics (aggregate only)

**Allowed Memory Access:**

| Layer | Read | Write |
|-------|------|-------|
| All Layers | ✅ | ❌ |
| Operational (listener_intel.json) | - | ✅ |
| Ephemeral | - | ✅ |

**Authority Level:**

| Authority Type | Level |
|----------------|-------|
| Information Power | ⭐⭐⭐⭐ (High influence via insights) |
| Mutation Authority | ❌ |

**Key Governance Rules:**

- ✅ Aggregate statistics ONLY (no individual PII)
- ✅ VIP detection via scores, not identities
- ✅ 30-day data retention max (auto-purge old intel)
- ❌ Never store X user IDs in long-term storage

---

### 4.3 EngagementBee

**Primary Function:**

- Process X mentions
- Verify payment injections (CRITICAL)
- Acknowledge tips
- Detect VIPs
- Route to appropriate bees

**Allowed Memory Access:**

| Layer | Read | Write |
|-------|------|-------|
| All Layers | ✅ | ❌ |
| Operational (engagement_log.json) | - | ✅ |

**Authority Level:**

| Authority Type | Level |
|----------------|-------|
| Social Authority | ⭐⭐⭐⭐ (High external impact) |
| Internal Mutation | ❌ (Can't modify manifesto/treasury directly) |

**Key Governance Rules:**

- ✅ Payment verification BEFORE instruction processing (P0 priority)
- ✅ Whitelist check + cryptographic signature (dual authentication)
- ✅ 5-minute payment window (must pay BEFORE posting instruction)
- ❌ No free instructions (even from whitelisted users - prevents abuse)

---

## 5. Tier 3: Operational Bees

### 5.1 Content & Research Bees

**ShowPrepBee**, **ClipCutterBee**, **TrendScoutBee**, **SocialPosterBee** remain largely as-is, with:

**Common Enhancements:**

1. Pre-flight check: Verify hive is healthy
2. Pre-flight check: Verify constitutional alignment
3. Execute actual work
4. Post-flight: Log to audit trail

---

## 6. Tier 4: Specialized Bees

### 6.1 SponsorHunterBee

**Enhanced Safeguards:**

- No forbidden industries (alcohol, tobacco, gambling, crypto, politics, pharma)
- No ads, only integrations
- Cultural fit check

---

## 7. Complete Bee Registry

### 7.1 Critical Tier (4 bees)

| # | Bee | Function |
|---|-----|----------|
| 1 | AdversaryBee | Simulates attacks, red team testing |
| 2 | FailureDetectorBee | Monitors failures, pulls Andon cord |
| 3 | ConstitutionalAuditorBee | Detects manifesto drift |
| 4 | StreamMonitorBee | Monitors broadcast health |

### 7.2 High Influence Tier (3 bees)

| # | Bee | Function |
|---|-----|----------|
| 5 | TreasuryGuardianBee | Enforces spending limits, prevents depletion |
| 6 | ListenerIntelBee | Privacy-preserving audience analytics |
| 7 | EngagementBee | Payment-verified instruction processing |

### 7.3 Operational Tier (4 bees)

| # | Bee | Function |
|---|-----|----------|
| 8 | ShowPrepBee | Content preparation |
| 9 | ClipCutterBee | Audio editing |
| 10 | TrendScoutBee | Trending topic detection |
| 11 | SocialPosterBee | X/Twitter posting |

### 7.4 Specialized Tier (6 bees)

| # | Bee | Function |
|---|-----|----------|
| 12 | SponsorHunterBee | Sponsorship discovery |
| 13 | PayoutProcessorBee | Refunds + dividends |
| 14 | WeatherBee | Weather integration |
| 15 | SportsTrackerBee | Sports updates |
| 16 | RadioPhysicsBee | Broadcast physics simulation |
| 17 | TrafficSponsorBee | Traffic reports |

---

## 8. Summary Statistics

| Metric | Value |
|--------|-------|
| **Total Bees** | 17 |
| **New Bees (v2.0)** | 4 (Adversary, FailureDetector, ConstitutionalAuditor, TreasuryGuardian) |
| **Enhanced Bees** | 4 (Engagement, ListenerIntel, StreamMonitor, SponsorHunter) |
| **Production Status** | Ready (with P0 + P1 implementation) |

---

## Document Control

| Property            | Value                          |
|---------------------|--------------------------------|
| **Document ID**     | BL-GOV-002                     |
| **Version**         | 2.0                            |
| **Effective Date**  | 2025-12-25                     |
| **Last Modified**   | 2026-01-15                     |
| **Author**          | Backlink Hive System           |
| **Approver**        | Oracle_Human                   |
| **Next Review**     | 2026-03-25                     |

### Revision History

| Version | Date       | Author               | Changes                                    |
|---------|------------|----------------------|--------------------------------------------|
| 1.0     | 2025-06-01 | Backlink Hive System | Initial bee specifications                 |
| 2.0     | 2025-12-25 | Backlink Hive System | Post-Red Team analysis, hardened governance |
| 2.1     | 2026-01-15 | Backlink Hive System | ISO compliance update, standardized format |
