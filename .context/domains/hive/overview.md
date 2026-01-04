# Domain: Core Hive

## Architecture

The Hive uses a **Stigmergic** architecture suitable for autonomous agent operations.

### Components

1. **Queen Orchestrator** (`hive/queen/orchestrator.py`):
    - The central loop.
    - Manages the "Heartbeat".
    - Spawns Bees based on schedules or triggers.
    - Does *not* store state itself; reads `honeycomb/state.json`.

2. **Honeycomb** (`hive/honeycomb/`):
    - **Shared Memory**. The only way Bees communicate.
    - `tasks.json`: Queue of pending actions.
    - `state.json`: Current global state (Mood, Playing Track, Active Bees).
    - `intel.json`: Long-term memory and gathered data.

3. **Bees** (`hive/bees/`):
    - Independent worker agents.
    - Inherit from `BaseBee`.
    - **Stateless execution**: They wake up, read tasks/state, execute, write results, and die (process terminates).

### Key Files

- `hive/main_service.py`: The FastAPI entry point for the "Face" (Web UI/Audio Stream).
- `monitor_stream.py`: Watchdog for the audio stream.
