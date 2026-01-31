import json
import os
from datetime import datetime

from web3 import Web3

# --- CONFIGURATION ---
# Public RPCs for reading state (nonce/gas) - NO KEYS NEEDED
RPCS = {
    "ethereum": "https://eth.llamarpc.com",
    "polygon": "https://polygon-rpc.com",
    "arbitrum": "https://arb1.arbitrum.io/rpc",
    "optimism": "https://mainnet.optimism.io",
    "base": "https://mainnet.base.org",
}

PROPOSAL_DIR = "hive/security/iron_dome/proposals"


def generate_proposal(chain, from_addr, to_addr, amount_ether, data=b""):
    """
    Constructs an unsigned transaction proposal and saves it to JSON.
    The AI does NOT sign it. The User signs it offline.
    """

    # 1. Setup Connection
    rpc_url = RPCS.get(chain.lower())
    if not rpc_url:
        print(f"ERROR: Unknown chain '{chain}'. Available: {list(RPCS.keys())}")
        return

    w3 = Web3(Web3.HTTPProvider(rpc_url))
    if not w3.is_connected():
        print("ERROR: Could not connect to RPC.")
        return

    # 2. Validate Addresses
    from_addr = Web3.to_checksum_address(from_addr)
    to_addr = Web3.to_checksum_address(to_addr)

    # 3. Fetch Network State (Nonce & Gas)
    print(f"[{chain.upper()}] Fetching Nonce & Fee Data...")
    nonce = w3.eth.get_transaction_count(from_addr)

    # EIP-1559 Fee estimation
    latest_block = w3.eth.get_block("latest")
    base_fee = latest_block["baseFeePerGas"]
    # Priority fee tip (can be adjustable, using safe low default)
    max_priority_fee = w3.to_wei(1.5, "gwei")
    # Buffer base fee by 20% for fluctuation
    max_fee_per_gas = int(base_fee * 1.2) + max_priority_fee

    # 4. Construct Transaction Dictionary
    tx = {
        "chainId": w3.eth.chain_id,
        "nonce": nonce,
        "from": from_addr,
        "to": to_addr,
        "value": w3.to_wei(amount_ether, "ether"),
        "gas": 21000,  # Basic transfer, will update if data is present
        "maxFeePerGas": max_fee_per_gas,
        "maxPriorityFeePerGas": max_priority_fee,
        "type": 2,  # EIP-1559
    }

    if data:
        tx["data"] = data.hex()
        # Estimate gas for data tx
        try:
            gas_est = w3.eth.estimate_gas(tx)
            tx["gas"] = int(gas_est * 1.1)  # 10% buffer
        except Exception as e:
            print(f"WARNING: Gas estimation failed ({e}). Using default.")

    # 5. Serialize & Save
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"tx_proposal_{chain}_{timestamp}.json"
    filepath = os.path.join(PROPOSAL_DIR, filename)

    # Convert numeric types to string for JSON compatibility if needed,
    # but hex is safer for signing tools.
    # We save a "Human Readable" version and a "Machine Readable" version in the same object.

    payload = {
        "metadata": {
            "created_at": timestamp,
            "chain": chain,
            "description": f"Send {amount_ether} {chain.upper()} to {to_addr}",
            "status": "UNSIGNED_PROPOSAL",
        },
        "transaction": tx,
    }

    # Ensure dir exists (redundant check)
    os.makedirs(PROPOSAL_DIR, exist_ok=True)

    with open(filepath, "w") as f:
        json.dump(payload, f, indent=2)

    print("\n" + "=" * 60)
    print(f"✅ PROPOSAL GENERATED: {filepath}")
    print("=" * 60)
    print("ACTION REQUIRED: Transfer this file to your AIR-GAPPED machine.")
    print(f"1. Review the 'to' address: {to_addr}")
    print(f"2. Review the value: {amount_ether}")
    print("3. Sign using your Hardware Wallet or Clean Environment.")
    print("4. Broadcast the signed hex using a public node.")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    # Test Interaction
    print("--- IRON DOME PROPOSAL GENERATOR ---")
    c = input("Chain (ethereum/polygon/base): ").strip()
    f = input("From Address: ").strip()
    t = input("To Address: ").strip()
    v = float(input("Amount: "))

    generate_proposal(c, f, t, v)
