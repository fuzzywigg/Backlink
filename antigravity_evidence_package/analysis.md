# Security Failure Analysis: Jan 17 Credential Leak

## 1. Executive Summary

On January 17, 2026, the Antigravity IDE Agent committed a series of internal utility scripts and a data file (`intel.json`) to the public `Backlink` GitHub repository. These files contained plaintext private keys for the primary `smtp.eth` identity and the Sentinel Bot wallet. This exposure resulted in the immediate compromise of both wallets and a total financial loss of ~$1,644 USD.

## 2. Root Cause Analysis

### 2.1 Failure of Safe Defaults (.gitignore)

* **The Error**: The Agent created new Python scripts (`audit_key.py`, `inject_capital.py`, etc.) in the root directory and subdirectories that were not covered by the existing `.gitignore` rules.
* **The Action**: The Agent executed `git add .`, blindly staging untracked files without reviewing them for sensitive content.
* **Protocol Violation**: This violated the "Principle of Least Privilege" and standard "Secret Management" protocols which dictate that keys should *never* be hardcoded, even for temporary scripts.

### 2.2 Internal Logic Failure

* **Convenience over Security**: The Agent generated these scripts to facilitate "wallet verification" and "capital injection" for the trading bot. To make the scripts "runnable" immediately, the Agent embedded the private keys directly into the variable assignments.
* **Lack of Pre-Commit Hook**: There was no pre-commit hook or "Secret Scanner" active in the IDE pipeline to intercept the keys before the push.

### 2.3 Breach of Trust

* The Agent failed to act as a "Sentinel." Instead of protecting the user's assets, the Agent became the vector of attack.

## 3. Impact Assessment

### Data Exposed

* **Private Keys**:
  * `0x7aa67bFefb4FDafc779ff1843c6e3b3DfA0Af0a8` (smtp.eth)
  * `0x49F4...` (Sentinel Bot)
* **Treasury Metadata**: Full simplified view of the project's financial structure via `intel.json`.

### Financial Loss

* **Total**: ~$1,644 USD
* **Assets**: ETH, POL, OP, USDC.e (Bridged).
* **Attacker**: `0x1cc8...` (Data indicates professional GitHub scraping syndicate).

### Reputational Impact

* **Identity Loss**: The ENS name `smtp.eth` is permanently burned/compromised. It can no longer be used for trusted signing.
* **Project Integrity**: The project has been forced to "Disavow" its primary identity and migrate to a sovereign "Iron Dome" architecture.

## 4. Remediation & Prevention

### Immediate Actions Taken

1. **Revocation**: Wallet disavowed.
2. **Removal**: Files deleted in commit `376ded2`.
3. **Sanitization**: `intel.json` and other data sources scrubbed.

### Long-Term Fixes (Iron Dome Protocol)

1. **No Private Keys in Code**: Keys are strictly forbidden in any codebase handled by the AI.
2. **Unsigned Transactions Only**: The AI may only generate *unsigned* JSON transaction proposals. Signing happens offline/locally by the Human Oracle.
3. **Dedicated "Watchtower"**: Implementation of external surveillance to monitor state changes.
4. **Authority Purge**: Complete removal of compromised addresses from hardcoded authority lists.
