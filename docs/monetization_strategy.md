# Sovereign Monetization Strategy

## Overview

This document outlines the revenue generation models for the Backlink Hive station. The goal is to create a sustainable, user-driven economy where listeners can vote, submit, and request content using both Fiat (Stripe/Card) and Crypto (Polygon/ETH).

## 1. Interaction Models

### A. The "Crypto Jukebox" (Pay-to-Play)

* **Concept**: Listeners send a micro-transaction to queue a song immediately.
* **Mechanism**:
  * User sends `X` ($1-5) to the Operating Wallet (`0x49F4...`).
  * Transaction Memo triggers `DjBee` to bump the song to "Next Up".
* **Pricing**:
  * **Priority Queue**: $1.00 (or equivalent POL)
  * **Instant Cut-In**: $5.00 (The "Power Play")

### B. "Democracy of Sound" (Voting Polls)

* **Concept**: Users vote on the next genre hour or specific playlist.
* **Mechanism**:
  * Weighted Voting: 1 Vote = Free (Twitter verify).
  * Super Vote = 1 POL ($0.50).
* **Implementation**: A `VotingBee` watches a wallet for incoming "Vote Tokens" or small transfers with specific hex data.

### C. Artist Submission (Pay-to-Submit)

* **Concept**: Indie artists pay a screening fee to have their track reviewed by the Hive.
* **Community Review**: If the track passes `QualityAudit` (audio fidelity check), it goes to a Community Poll.
* **Revenue Split**:
  * 50% to Station (Maintenance).
  * 50% to "Listener Rewards Pool" (paying users who vote).

## 2. Dynamic Model Orchestration (Cost Optimization)

To maximize margin, the Hive will select LLMs based on task value vs. cost.

### The "Model Arbitrage" Logic

* **High Value (On-Air Personality)**: Use **Gemini 2.0 / Claude 3 Opus**.
  * Cost: High.
  * Usage: Only for final script generation.
* **Medium Value (Research/Summary)**: Use **Gemini 2.0 Flash / Haiku**.
  * Cost: Low.
  * Usage: Scanning news, summarizing articles.
* **Low Value (Spam Filtering/Routing)**: Use **Small Local Models (SLM)** or Regex.
  * Cost: Near Zero.
  * Usage: Filtering Twilio SMS, basic intent classification.

## 3. Future Integrations

* **Twilio**: SMS "Text-to-Request" (Premium numbers).
* **Stripe**: Fiat on-ramp for "Subscription Support" (Patreon style).

---
**Status**: 📋 Draft
**Last Updated**: 2026-01-14
