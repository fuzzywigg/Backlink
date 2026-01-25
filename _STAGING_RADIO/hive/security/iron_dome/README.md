# IRON DOME: Sovereign Security Protocol

**Status:** ACTIVE
**Version:** 3.0 (Post-Purge)

## Core Mandate

The Iron Dome ensures that NO sensitive keys (Private Keys, API Creds) are ever exposed to the runtime environment or the AI agent.

## Protocols

1. **Air-Gapped Signing:**
    * Transactions are generated as "Unsigned Proposals" (JSON).
    * Proposals are moved to a secure device (Hardware Wallet / Clean Laptop).
    * Signing happens OFFLINE.
    * Broadcast happens via public nodes.

2. **The Beehive (Context Layer):**
    * Security decisions are informed by the local vector memory (`hive/products/beehive`).
    * This ensures the "Hunter" and "Sentinel" have context without having keys.

3. **Honeypot Defense:**
    * Decoy keys are deployed to catch scrapers.
    * See `hive/products/honeycomb_core` for details.

## Recent Updates

* **Jan 20 2026:** Integration with 64GB RAM Workstation specific optimizations.
* **Jan 20 2026:** "Beehive" Local Vector Memory initialized to provide safe, key-less context.
