# Emergency Bridging Protocol: zkEVM to PoS

## 🚨 The Issue: Network Mismatch

- **Your Funds ($619.20 USDC.e)** are on **Polygon zkEVM**.
- **The Bot/Polymarket** lives on **Polygon PoS**.
- **Result:** The bot sees $0.00 because it is looking at the wrong blockchain.

## 🛠️ The Fix: Bridge to Polygon PoS

You must move the funds from the "zkEVM City" to the "PoS City".

### Option 1: Official Polygon Portal (Recommended)

1. Go to **[portal.polygon.technology](https://portal.polygon.technology/bridge)**.
2. Connect your wallet (`0x49F4...`).
3. Select **Bridge**.
4. **From:** Polygon zkEVM
5. **To:** Polygon PoS
6. Select **USDC.e** as the token.
7. Click **Bridge**.

### Option 2: Aggregators (Faster/Cheaper)

- **[Jumper.exchange](https://jumper.exchange)** (by Li.Fi)
- **[Bungee.exchange](https://bungee.exchange)** (by Socket)

## ⚠️ Requirements

- You need a small amount of **ETH on zkEVM** to pay for the "send" gas.
- You need a small amount of **POL (Matic) on PoS** to pay for the "receive" gas (sometimes).

## Verification

Once bridging is complete (usually 15-20 mins for official, or minutes for aggregators), the Sentinel Bot will automatically detect the funds and show:
`[SENTINEL] INFO - Wallet Balance: $619.20 USDC`
