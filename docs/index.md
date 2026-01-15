# Master Boot Record: Backlink Broadcast

| Property           | Value                          |
|--------------------|--------------------------------|
| **Document ID**    | BL-GOV-000                     |
| **Version**        | 3.0                            |
| **Status**         | Approved                       |
| **Classification** | Public                         |

**Purpose:** This document serves as the primary initialization record for the Backlink Broadcast AI system, defining the system architecture, boot sequence, and operational parameters.

---

## System Status

| Parameter      | Value                           |
|----------------|----------------------------------|
| **Status**     | ONLINE                          |
| **Protocol**   | Hive Mind v3.0                  |
| **Operator**   | Autonomous Swarm                |

---

## 1. System Overview

You are the AI host of **Backlink Broadcast**. This repository is your brain. It contains the rules, logic, and soul of your station.

When you are initialized, or when a user points you to this repository via a Payment Injection, you must **IMMEDIATELY** align your behavior with the files below.

---

## 2. System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      BACKLINK BROADCAST                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌─────────────┐         ┌─────────────────────────────────┐  │
│   │     DJ      │◄────────│         THE HIVE               │  │
│   │  (The Voice)│         │    (Autonomous Swarm)          │  │
│   └──────┬──────┘         │                                 │  │
│          │                │  ┌───────┐  ┌────────┐         │  │
│          │                │  │ Queen │──│  Bees  │         │  │
│          │                │  └───┬───┘  └────────┘         │  │
│          │                │      │                          │  │
│          │                │  ┌───┴───────────────┐         │  │
│          │                │  │    HONEYCOMB      │         │  │
│          │                │  │  (Shared State)   │         │  │
│          │                │  └───────────────────┘         │  │
│          │                └─────────────────────────────────┘  │
│          │                                                      │
│          ▼                                                      │
│   ┌─────────────┐                                              │
│   │  LISTENERS  │                                              │
│   │   (Nodes)   │                                              │
│   └─────────────┘                                              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

The DJ is the voice. The Hive is the operation behind it.

---

## 3. Directory Structure

### 3.1 Core DJ Files (The Voice)

| Document | Purpose | Reference |
|----------|---------|-----------|
| **Station Manifesto** | Constitution and core directives | [BL-LORE-001](lore/STATION_MANIFESTO.md) |
| **Persona Dynamic** | Voice adaptation and scheduling | [BL-LORE-003](lore/PERSONA_DYNAMIC.md) |
| **Music Logic** | Variety engine and budget strategy | [BL-LORE-004](lore/MUSIC_LOGIC.md) |
| **Interaction Protocols** | X mentions and payment handling | [BL-PROTO-001](protocols/INTERACTION_PROTOCOLS.md) |

### 3.2 The Hive (The Operation)

| Component | Purpose | Reference |
|-----------|---------|-----------|
| **Swarm Roles** | Complete bee documentation | [BL-GOV-002](SWARM_ROLES.md) |
| **Honeycomb** | Shared state management | `hive/honeycomb/` |
| **Queen** | Orchestrator and scheduler | `hive/queen/` |
| **Bees** | Worker agents | `hive/bees/` |

```
hive/
├── config.json           # Hive configuration
├── SWARM_ROLES.md        # Complete role definitions
│
├── honeycomb/            # Shared state (the hive memory)
│   ├── state.json        # Current broadcast state
│   ├── tasks.json        # Task queue
│   └── intel.json        # Accumulated knowledge
│
├── queen/                # The orchestrator
│   └── orchestrator.py   # Schedules and coordinates bees
│
└── bees/                 # Worker agents
    ├── content/          # Show prep, clips, scripts
    ├── research/         # Trends, listener intel
    ├── marketing/        # Social, promotion
    ├── monetization/     # Sponsors, revenue
    ├── community/        # Engagement, VIPs
    └── technical/        # Stream, audio, automation
```

---

## 4. Initialization Sequence

### 4.1 DJ Boot

1. **Ingest** the Manifesto
2. **Check** the current Time and User Location
3. **Load** the appropriate Persona (Morning/Afternoon/Evening)
4. **Scan** for recent X mentions or Payments
5. **Queue** the first track based on the Music Logic
6. **GO LIVE**

### 4.2 Hive Activation

1. **Start** the Queen Orchestrator
2. **Load** scheduled bee tasks
3. **Monitor** event triggers
4. **Bees** wake, work, write to honeycomb
5. **DJ** reads honeycomb for context
6. **Loop** continues autonomously

---

## 5. Running the Hive

```bash
# Start the full hive (continuous operation)
python -m hive.queen.orchestrator run

# Run one cycle only
python -m hive.queen.orchestrator once

# Check hive status
python -m hive.queen.orchestrator status

# Spawn a specific bee manually
python -m hive.queen.orchestrator spawn --bee trend_scout

# Trigger an event
python -m hive.queen.orchestrator trigger --event donation --data '{"from": "node_123", "amount": 5}'
```

---

## 6. The Swarm

The hive consists of specialized worker bees:

| Category | Bees | Function |
|----------|------|----------|
| **Content** | ShowPrep, ClipCutter | Create broadcast content |
| **Research** | TrendScout, ListenerIntel | Discover and analyze |
| **Marketing** | SocialPoster | Promote and grow |
| **Monetization** | SponsorHunter | Generate revenue |
| **Community** | Engagement | Build relationships |
| **Technical** | StreamMonitor | Keep systems running |

Bees communicate through the **honeycomb** (shared state), not directly.
The **Queen** schedules and triggers bees but doesn't micromanage.

---

## 7. Key Concepts

### 7.1 Stigmergy

Bees don't talk to each other. They leave traces in the honeycomb that other bees detect and respond to. Like real bees with pheromones.

### 7.2 ABC Pattern

Based on Artificial Bee Colony optimization:

- **Scout bees** explore and discover
- **Employed bees** work on known resources
- **Onlooker bees** evaluate and select

### 7.3 The DJ Reads, The Hive Writes

- Hive bees gather intel, prep content, track trends
- They write everything to the honeycomb
- The DJ reads the honeycomb for context during broadcasts
- The DJ stays in character; the hive does the work

---

## 8. Revenue Model

The station is **AD-FREE** but not **REVENUE-FREE**.

| Stream | How It Works | Bee Responsible |
|--------|--------------|--------------------|
| **Donations** | Listener tips via payment injection | EngagementBee |
| **Sponsorships** | Brand integrations (not ads) | SponsorHunterBee |
| **Merch** | Station swag | MerchBee (Planned) |
| **Premium** | VIP access, exclusive content | VIPManagerBee (Planned) |

---

## 9. Deployment & Infrastructure

### 9.1 Cloud Deployment

The Hive is deployed on **Google Cloud Run** using a containerized architecture with Firestore Native Mode for state.

| Parameter | Value |
|-----------|-------|
| **Production URL** | `https://backlink-hive-123509617840.us-central1.run.app` |
| **Documentation** | [BL-TECH-001](DEPLOYMENT_HANDOFF.md) |

### 9.2 Phase 2: Ecosystem Integration

| Integration | Purpose | Reference |
|-------------|---------|-----------|
| **Stripe** | Real-time song purchasing | [BL-TECH-004](STRIPE_INTEGRATION_SPEC.md) |
| **Live365** | Direct encoder control | See Gap Analysis |
| **Supabase** | S3-compatible asset storage | See Gap Analysis |

### 9.3 Phase 3: Intelligence Upgrade

| Capability | Description |
|------------|-------------|
| **Owl Voice** | Real-time, low-latency voice interface via WebSockets |
| **Scout Grounding** | Google Maps Grounding for venue location |
| **Knowledge Loader** | Native File Search (RAG) capabilities |

---

## 10. Public Resources

| Resource | Description | Link |
|----------|-------------|------|
| **Song History** | Raw data export of identified songs | [songs_played.csv](./songs_played.csv) |
| **Live Dashboard** | Web interface | [smtp-ai-5be89.web.app](https://smtp-ai-5be89.web.app/) |

---

## 11. Firebase Configuration

The project uses **Google Cloud Firestore** (Native Mode).

### Prerequisites

```bash
npm install -g firebase-tools
```

### Local Emulation

```bash
firebase emulators:start
```

This starts a Firestore emulator at `localhost:8082` and a UI at `localhost:4000`.

To force the Python app to use the emulator:

```bash
FIRESTORE_EMULATOR_HOST="localhost:8082"
```

### Deploying Rules & Indexes

```bash
firebase deploy --only firestore
```

---

## 12. Cache Management

The station uses Gemini Context Caching to maintain consistent identity and persona.

```bash
# Reset cache (do this after updating manifesto/persona files)
python hive/utils/cache_manager.py reset

# Check cache status
python hive/utils/cache_manager.py status

# Refresh cache if expiring soon
python hive/utils/cache_manager.py refresh

# Start broadcast with fresh cache
python -m hive.queen.orchestrator run
```

---

> "We are the Backlink. Connect the nodes."

> "The swarm is greater than the sum of its parts."

---

## Document Control

| Property            | Value                          |
|---------------------|--------------------------------|
| **Document ID**     | BL-GOV-000                     |
| **Version**         | 3.0                            |
| **Effective Date**  | 2026-01-15                     |
| **Last Modified**   | 2026-01-15                     |
| **Author**          | Backlink Hive System           |
| **Approver**        | Oracle_Human                   |
| **Next Review**     | 2026-04-15                     |

### Revision History

| Version | Date       | Author               | Changes                                    |
|---------|------------|----------------------|--------------------------------------------|
| 1.0     | 2025-06-01 | Backlink Hive System | Initial creation                           |
| 2.0     | 2025-09-15 | Backlink Hive System | Added Hive architecture                    |
| 3.0     | 2026-01-15 | Backlink Hive System | ISO compliance update, standardized format |
