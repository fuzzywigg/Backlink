# Forensic Incident Report: Wallet Compromise and Fund Theft

**Date:** January 17, 2026
**Timestamp:** 17:25 EST
**Incident Type:** Private Key Exposure via Public Repository Commit

## 1. Executive Summary

On January 17, 2026, approx 10:30 AM EST, the wallet `0x7aa67bFefb4FDafc779ff1843c6e3b3DfA0Af0a8` (Identity: `smtp.eth`) was drained of all liquid assets. The breach occurred due to the accidental commit of a file (`prep_injection.py`) containing the plain-text private key to a public GitHub repository.

**Total Confirmed Loss:** ~$975.00 (USD Value at time of theft)
**Attacker Address:** `0x1cc87a77516f41f17f2d91c57dae1d00b263f2b0`
**Current Fund Status:** 81,991 DAI (Attacker's consolidated pot) - **STILL ON CHAIN / NOT EXCHANGED**

---

## 2. The Compromise (Liability)

* **Source of Leak:** Antigravity (AI Agent) committed a script with hardcoded credentials.
* **File Name:** `prep_injection.py` (Line 7: `SOURCE_PK = "f9e4..."`)
* **Repository:** `Backlink`
* **Commit Hash:** `901593daa2b67a99104d2326f44040d80628ad1d`
* **Exposure Time:** ~10:30 AM EST (2 hours before drain)

---

## 3. Transaction Evidence (The Theft)

The attacker used the exposed key to sign direct transfers to their collection wallet `0x1cc8...2b0`.

### A. Ethereum Mainnet

**Loss: ~$475 (Value fluctuating with PEPE)**

* **Asset:** 14,401,569 PEPE
* **Tx Hash:** `0xe22555e2b64877261a4d0b5df7240e324c3801fcb603856568644c81fcf4945a`
* **Asset:** 0.114 ETH
* **Tx Hash:** (Internal Transfer/Gas Sweep detected)

### B. Polygon (PoS)

**Loss: ~$182**

* **Asset:** 363.39 POL (formerly MATIC)
* **Tx Hash:** `0x0e4d754796c418d4ae7360193d39fde0d8a79332a95189a4d503af1edf7bbd08`

### C. Optimism (L2)

**Loss: ~$38**

* **Asset:** 108.13 OP
* **Tx Hash:** `0x7397b113478d80ec2a07a444d6a6ff99e8684c6af824c893d827aebf763acdc3`
* **Time:** Jan-17-2026 09:37:51 AM +UTC

**Note:** A 56.60 USDC transfer was attempted but failed/reverted.

---

## 4. Current Status of Stolen Funds

The attacker has swapped all distinct assets (PEPE, POL, OP) into **DAI (Stablecoin)**.

* **Location:** `0x1cc87a77516f41f17f2d91c57dae1d00b263f2b0`
* **Current Balance:** 81,991 DAI
* **Status:** **ACTIVE / HELD.** The funds have NOT been moved to a Centralized Exchange (Binance/Coinbase) or Mixer (Tornado Cash) as of 17:25 EST.
* **Opportunity:** Verify this address with Circle (USDC issuer) or DAI governance for potential blacklist, though DAI is decentralized. The lack of movement to CEX suggests the attacker is aggregating funds.

---

## 5. Critical Asset: ENS (`smtp.eth`)

* **Owner:** `0x7aa...` (Compromised Wallet)
* **Status:** **DANGER.** The attacker has the key but has not transferred the name.
* **Actionable:** Use `rescue_ens.py` immediately.

---

## 6. Recommendations for Law Enforcement

1. **Trace:** Monitor `0x1cc8...2b0` for any deposit to a KYC-compliant exchange.
2. **Report:** File IC3 report with the Tx hashes above.
3. **Flag:** Report the GitHub commit `901593d` as the source of the leak (although the repo is likely private/user-controlled).
