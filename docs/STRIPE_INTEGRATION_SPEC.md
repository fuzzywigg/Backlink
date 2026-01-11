# Stripe Integration Specification: Andon FM Protocol

**Version**: 1.0
**Source**: Andon FM Deep Research
**Status**: Planning (Phase 2)

## Overview

The Hive uses Stripe's **PaymentIntents API** (not Subscriptions) for one-time song purchases. Each track is a Stripe **Price Object** with extensive metadata.

## 1. Data Schemas

### Stripe Price Object (Song)

Each purchasable track must match this schema in Stripe:

```json
{
  "object": "price",
  "type": "one_time",
  "billing_scheme": "per_unit",
  "unit_amount": 199,      // $1.99
  "currency": "usd",
  "active": true,
  "metadata": {
    "station_id": "thinking-frequencies",  // Agent Filter
    "song_title": "Imagine Remastered 2010",
    "artist_name": "John Lennon",
    "genre": "Rock",
    "duration_seconds": "183",
    "isrc": "GBUM71234567",                // Critical for royalties
    "license_type": "full_streaming_rights"
  }
}
```

### Transaction Ledger (Firestore)

When `payment_intent.succeeded` fires, this record is written to `stations/{station_id}/transactions`:

```javascript
{
  "timestamp": 1703001600000,
  "type": "song_purchase",
  "price_id": "price_1ScAl1Re5lTj445Ny1fC1Vk8",
  "amount_usd": 1.99,
  "song_title": "Imagine Remastered 2010",
  "artist": "John Lennon",
  "agent": "ThinkingFreq",
  "idempotency_key": "song_price_1Sc..._1703001600"
}
```

## 2. Agent Purchase Flow

1. **Discovery**: Agent queries Stripe API (`v1/prices`) filtering by `lookup_key="{station_id}"` and `active=true`.
2. **Decision**: Agent evaluates `metadata` (Genre, BPM) against Station Manifesto and checks `treasury.balance`.
3. **Execution**: Agent calls `stripe.PaymentIntent.create()`:
    * `amount`: derived from Price object.
    * `metadata`: includes `song_price_id` and `station_id`.
    * `idempotency_key`: `song_{price_id}_{timestamp}` (Required).
4. **Verification**: Agent waits for Firestore balance update (triggered by Webhook).

## 3. Webhook Security Strategy

The `POST /webhook` endpoint in `main_service.py` is the **Root of Trust**.

### Requirements

1. **Signature Verification**: MUST use `stripe.Webhook.construct_event(payload, sig, secret)`.
2. **Secret Management**: `STRIPE_WEBHOOK_SECRET` must be loaded from env (Secret Manager).
3. **Event Handling**:
    * `payment_intent.succeeded`: Credit song to library, deduct balance.
    * `payment_intent.payment_failed`: Trigger "Retry Logic" (Exponential Backoff).

## 4. Recurring Issues & Mitigation

| Issue | Cause | Mitigation |
| :--- | :--- | :--- |
| **24h Retry Loop** | Office-hours availability | Exponential backoff in `TreasuryGuardianBee`. |
| **Double Charge** | Network retries | Strict `idempotency_key` generation. |
| **Metadata Drift** | Stripe UI edits | Agents trust `metadata` as source of truth. |

## 5. Implementation Checklist

* [ ] Enables `stripe` library in `requirements.txt`.
* [ ] Create `hive/utils/stripe_client.py` wrapper.
* [ ] Implement `webhook_handler` in `main_service.py`.
* [ ] Update `DjBee` to use `stripe.Price.list` for discovery instead of mock lists.

## 6. The Gatekeeper Protocol (The "Piano Bar" Method)

**Status:** Planned (Critical Fix for "Jukebox Jam")

We are replacing the "Strict Sanitization" model with a **Verification & Priority** model to ensure no paying customer is ignored due to a typo.

### 6.1 The "Tip Jar" Priority (Paid vs. Free)

Like a piano bar, money talks.

1. **High Priority (Paid):** Requests with a verified `PaymentIntent` ID. These jump to the front of the queue.
2. **Low Priority (Shouts):** Requests from Twitter/Socials without payment. These are ignored unless the Paid Queue is empty.

### 6.2 Verification (The Lookup)

Instead of blindly rejecting "weird" text, we use it to search.

* **Input:** "Song With; Weird-Chars (Remix)"
* **Action:** The system calls the **Spotify API Search**.
* **Result:**
  * **Match Found:** We discard the user's messy text and use the **Clean Official Title/Artist** from Spotify. This sanitizes the data *for* us.
  * **No Match (The "Crowd Protocol"):** We do NOT hide this in a private dashboard.
    * **Action:** `EngagementBee` posts to **Twitter**: *"@User sent $5 for '[Input]' but I can't find it. Help? Reply with the Spotify link."*
    * **Resolution:** The Agent monitors replies. If a trusted user (or the buyer) replies with a valid Spotify URL, the request is updated and moved to `VERIFIED`.
    * **Benefit:** Keeps the community engaged and turns a "bug" into a "collaborative moment."

### 6.3 The FIFO Queue (The Hopper)

We cannot process 50 requests simultaneously.

1. **Ingest:** Requests enter `honeycomb/request_queue.json` with a `priority` score.
2. **State:** Requests have a `status`: `PENDING` -> `VERIFIED` -> `PLAYED`.
3. **Throttle:** The `DjBee` only pulls **ONE** item from `VERIFIED` at a time.
4. **Grace Period:** Enforce a 30-second "cool down" between identifying new purchases to allow the backend to settle.

### 6.4 "Slot Full" Logic

If `honeycomb/request_queue.json` > 50 items:

* Temporarily disable `payment_intent` creation (API returns 503).
* Prevents the "machine" from eating coins it cannot honor.
