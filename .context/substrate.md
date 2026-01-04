# Context Substrate: Backlink Hive

This repository contains **Backlink Broadcast**, an autonomous AI radio station powered by a stigmergic hive mind of agents.

## 🗺️ High-Level Map

| Domain | Description | Context File |
|---|---|---|
| **Core Hive** | The autonomous agent swarm (Queen, Bees, Honeycomb). | [.context/domains/hive/overview.md](./domains/hive/overview.md) |
| **Infrastructure** | Cloud Run, Docker, Firebase, and Deployment. | [.context/domains/infrastructure/overview.md](./domains/infrastructure/overview.md) |
| **Identity & Lore** | The DJ Persona, Economic Rules, and Constitution. | [config/lore/AGENTS.md](../config/lore/AGENTS.md) |
| **Documentation** | Public facing documentation. | [docs/index.md](../docs/index.md) |

## 🚀 Quick Start

- **Orchestrator**: `python -m hive.queen.orchestrator run`
- **Web Service**: `uvicorn hive.main_service:app --reload`
- **Tests**: `pytest`

## 🧠 Core Concepts

1. **Stigmergy**: Agents do not communicate directly. They read/write to `hive/honeycomb/*.json` files.
2. **Queen/Worker**: The `QueenOrchestrator` schedules tasks; `Bees` execute them.
3. **Strict JSON**: All LLM tool outputs must be valid JSON.
