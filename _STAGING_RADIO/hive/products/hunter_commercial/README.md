# THE HUNTER: Commercial Watchtower

**Version 1.0 (Sovereign release)**

## "Turn Your Tragedy Into A Trap"

The Hunter is a verified security tool born from the January 17, 2026, security incident at Backlink Hive. It allows you to monitor compromised Ethereum-based addresses and detect attacker activity in real-time.

### Why use The Hunter?

If your private key is exposed, bots will sweep assets instantly. However, attackers often use compromised wallets as "mules" or simply hold assets (like NFTs) hostage.
**The Hunter** gives you eyes on the enemy.

### Features

* **Daemon Mode:** Runs 24/7 in the background.
* **Multi-Chain:** Monitors ETH Mainnet and Polygon (configurable).
* **Balance Watch:** Detects any incoming funds (bait or mistake).
* **Nonce Watch:** Detects outgoing transactions (Attacker activity).
* **JSON Logging:** Evidence-grade logging to `evidence_locker.json`.

### Quick Start

1. **Install:** Run `install_hunter.bat` (Windows) or `pip install web3`.
2. **Configure:** Edit `hunter_config.json`:

    ```json
    {
      "rpc_url": "https://eth.llamarpc.com",
      "targets": {
        "0xYourAddress...": "My Compromised Wallet",
        "0xAttacker...": "The Thief"
      }
    }
    ```

3. **Run:** `python hunter.py`

### Sovereignty Note

This tool is **clean**. It requires NO private keys to operate. It only reads public ledger data. It is safe to run on any machine.
