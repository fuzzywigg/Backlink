# Andon Labs Evals FM Radio & Physical Bridge

**Strategic Note:** This document records the integration roadmap for the "Physical Bridge" between the Backlink Hive and the upcoming Andon Labs AI Radio hardware.

## Quick Summary

* **Target Release:** Early 2026
* **Hardware:** Andon Labs Evals FM Radio
* **Key Repo:** `https://github.com/AndonLabs/inspect_ai_fork`
* **Partner Context:** OpenAI hardware projects.

## The Physical Bridge Concept

The "Physical Bridge" refers to the interface layer that allows the digital `inspect_ai` evaluation framework to communicate with and control physical radio hardware.

### Technical Merits

1. **Hardware-in-the-Loop (HIL):** The `inspect_ai_fork` enables real-time evaluation of AI agents interacting with physical RF environments, not just simulated streams.
2. **Telemetry Ingestion:** The Hive will be able to receive signal strength, frequency engagement, and hardware status from the physical radio, treating it as a high-fidelity sensor node (similar to a "super-scout").
3. **Active Control:** The bridge likely allows the AI (the Hive's "DJ" or "Queen") to actively tune, transmit (where licensed), or modify the radio's physical parameters programmatically.

## Strategic Value

We "exploit the value from knowing this" by:

1. **Pre-integration:** Designing the Hive's `StreamMonitorBee` and `DjBee` to accept "Hardware Telemetry" payloads now, before the hardware ships.
2. **Architecture Alignment:** Adopting the `inspect_ai` evaluation patterns for our own internal audits, ensuring minimal friction when the hardware arrives.
3. **First Mover Advantage:** Being ready to deploy the Hive implementation onto the "Andon Labs Evals FM Radio" immediately upon its early 2026 release.

## Action Items

* [ ] Monitor `AndonLabs/inspect_ai_fork` for updates.
* [ ] Review `inspect_ai` (original) to understand the base classes for "Scorers" and "Solvers" that will likely be extended for hardware.
* [ ] Define a `HardwareState` schema in `honeycomb/intel.json` to prepare for this data.
* [ ] Evaluate `AndonLabs/multiagent-inspect` for swarm testing (See [EVAL_MULTIAGENT_INSPECT.md](./EVAL_MULTIAGENT_INSPECT.md)).
