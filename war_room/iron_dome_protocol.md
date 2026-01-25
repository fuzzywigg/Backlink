# IRON DOME PROTOCOL: The Air-Gap Signing Standard

**Severity:** MANDATORY
**Scope:** All Financial Transactions in V3 Architecture

## THE PROBLEM

The `smtp.eth` compromise happened because a Private Key was:

1. Live on a hot wallet.
2. Accessible to the AI code (`prep_injection.py`).
3. Committed to a repo.

## THE SOLUTION: "PROPOSE / SIGN / BROADCAST" SEPARATION

We are moving to a **3-Step Workflow** for all future operations.

### STEP 1: PROPOSE (The AI's Role)

* The AI (Antigravity/Bot) **never** sees a private key.
* The AI constructs an **Unsigned Transaction Object** (The "Proposal").
* *Example:* "I propose sending 100 USDC to User."
* **Output:** A JSON file `tx_proposal_001.json`.

### STEP 2: SIGN (The User's Role - AIR GAPP)

* **Device:** Hardware Wallet (Ledger/Trezor) OR an Air-Gapped Clean Phone.
* **Action:**
    1. User reads `tx_proposal_001.json`.
    2. User reviews the destination and amount.
    3. User signs it **offline**.
* **Output:** A "Signed Raw Transaction" string (Hex).

### STEP 3: BROADCAST (The Network's Role)

* The AI takes the **Signed Hex** string.
* The AI broadcasts it to the RPC node.
* **Security:** Even if the AI is rogue or hacked, it cannot change the transaction because the signature would break. It cannot steal funds because it doesn't have the key.

## IMPLEMENTATION CHECKLIST

- [ ] Remove `web3.eth.account.sign_transaction` from all AI scripts.
* [ ] Create `proposal_generator.py` for the AI.
* [ ] Enforce Hardware Wallet usage for the new `0x9d27...` Safe Wallet.
