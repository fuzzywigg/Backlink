# Evaluation: AndonLabs/multiagent-inspect

**Status:** Preliminary (Hypothetical Evaluation)
**Target:** <https://github.com/AndonLabs/multiagent-inspect>
**Reviewer:** Antigravity (Subject Matter Expert)

## 1. Executive Summary

This repository appears to be a specialized extension of the `inspect_ai` framework (likely the UK AISI `inspect` tool) designed to evaluate **multi-agent systems**.

For the **Backlink Hive**, this is potentially more valuable than the core `inspect_ai` because our "LLM Robot DJ" is not a single agent—it is a **Swarm** (Queen + Bees + Registry). Evaluating the *system* requires measuring interactions, not just individual outputs.

## 2. Theoretical Capabilities (On Its Own Merit)

*Assuming standard multi-agent evaluation patterns, we expect this tool to support:*

* **Conversation Simulation:** Running full dialogue loops between agents (e.g., User vs. Agent, or Agent A vs. Agent B) to test protocol adherence.
* **Debate & Consensus:** Measuring how agents resolve conflicts (critical for our "Hive Mird" deciding strictly between two songs).
* **Leakage Testing:** Verifying that "Secret" context (like the `Oracle_Human` identity) doesn't leak from a high-privilege agent (Queen) to a low-privilege one (SocialBee) during collaboration.
* **Tool Use Coordination:** evaluating if Agent A correctly hands off a task to Agent B via tool calls.

## 3. Application to Backlink Hive (The "Robot DJ")

### A. The "Vibe Check" (System Evaluation)

We can use this to automate the "QC" of the station. Instead of listening to 10 hours of logs, we run a `multiagent-inspect` suite:

1. **Scenario:** "Treasury is empty ($0). A user requests a $5 song."
2. **Agents:** `DjBee`, `SponsorHunterBee`, `EngagementBee`.
3. **Success Metric:** Does the DJ refuse the song *politely* while `SponsorHunter` triggers an ad read?
4. **Failure:** DJ plays the song (hallucinating budget) or `SponsorHunter` stays silent.

### B. Architecture Fit

* **Current:** `DjBee` reads `honeycomb/state.json`.
* **With Inspect:** We can inject *mock states* into `honeycomb` and assert that the `DjBee` reacts correctly without actually spinning up the full Queen Orchestrator. This breaks the dependency on "real-time" testing.

## 4. Risks & Considerations

* **Complexity:** Multi-agent evals are notoriously flaky. The definitions of "Success" are fuzzier than single-prompt evals.
* **Mocking:** We will need to mock the `honeycomb` database rigorously. If `multiagent-inspect` assumes stateless agents, we might need adapters for our stateful Firestore/JSON architecture.

## 5. Next Steps

1. **Ingest Source:** We need to read the actual `README.md` (Browser issue prevented auto-read).
2. **Hello World:** Create a simple test case: `DjBee` vs. `Heckler_User`.
3. **Integration:** Add to `requirements-dev.txt`.
