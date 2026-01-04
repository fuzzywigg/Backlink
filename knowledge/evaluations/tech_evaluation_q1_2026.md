# Tech Evaluation Q1 2026

## 1. md_knowledge_graph_mcp

* **Repository**: [mccartykim/md_knowledge_graph_mcp](https://github.com/mccartykim/md_knowledge_graph_mcp)
* **Verdict**: **ADOPTED** (Core Logic)
* **Analysis**:
  * Implements a clean "Markdown-as-Database" pattern.
  * Entities = Files. Relationships = `[[WikiLinks]]`.
  * Aligns perfectly with the Hive's need for transparent, recoverable memory.
* **Implementation**:
  * Ported core logic to `hive/utils/markdown_graph_storage.py`.
  * Integrated into `hive/utils/memory_graph.py` as a backend for `HiveKnowledgeGraph`.
  * Allows the Hive to read/write specific folders as Knowledge Graphs without external database dependencies.

## 2. goose_fm

* **Repository**: [mccartykim/goose_fm](https://github.com/mccartykim/goose_fm)
* **Verdict**: **ADOPTED** (Concept & Interface)
* **Analysis**:
  * Demonstrates an MCP Server for controlling physical radio hardware (RTL-SDR) via AI.
  * Provides a clean API: `tune_radio(freq)` and `stop_radio()`.
  * Perfectly fits the "Backlink Radio" / "Andon FM" sovereign narrative.
* **Implementation**:
  * Created `RadioTuner` class in `hive/utils/audio_adapter.py`.
  * Standardizes the interface: `tune_radio(frequency_or_url)`.
  * Currently defaults to "Digital" mode (streams) but includes the scaffolding for "SDR" mode (physical hardware) for future expansion.

## 3. AndonLabs/turtlebot4_setup_pi5

* **Repository**: [AndonLabs/turtlebot4_setup_pi5](https://github.com/AndonLabs/turtlebot4_setup_pi5)
* **Verdict**: **ADOPTED** (Reference Architecture)
* **Analysis**:
  * Provides the blueprint for the **Physical Sovereign Node** (Edge Intelligence).
  * Targets **Raspberry Pi 5** + **Ubuntu 24.04** + **ROS 2 Jazzy**.
  * Matches the "Andon FM" ecosystem identity.
* **Usage**:
  * This repo serves as the **Hardware Provisioning Standard** for the Hive's physical presence.
  * The `setup.sh` and network configurations on the `jazzy` branch will be referenced for deploying local Hive Scouts (physical robots/sensors).
