# 🤖 Agent Guidelines

You are entering the **Backlink Hive** repository. This is a complex autonomous agent system.

## 🧠 Your Primer

1. **Read the Substrate**: Always check `.context/substrate.md` to orient yourself.
2. **Respect the Architecture**:
    - Do NOT suggest direct agent-to-agent communication. Use the `honeycomb` (JSON state).
    - Do NOT assume standard web app patterns; this is an *asynchronous agent swarm* with a web frontend.
3. **Code Style**:
    - Python 3.11+
    - Strict typing (`mypy` compatible preferred).
    - Google Style Docstrings.
    - **JSON is King**: All tool outputs must be JSON.

## 📍 Key Locations

- **Agent Logic**: `hive/bees/`
- **Orchestration**: `hive/queen/`
- **Configuration**: `config.json` and `.env`
