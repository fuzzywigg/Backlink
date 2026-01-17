"""
LIQUIDITY INJECTOR
Moves MATIC from Source Wallet -> Bot Wallet
Then Bot automatically swaps MATIC -> USDC (Simulation for now, transfer is real)
"""
from web3 import Web3
import sys
import os
from dotenv import load_dotenv

# CONFIGURATION
# CONFIGURATION
# SOURCE_PK loaded from environment variable for security
load_dotenv()
SOURCE_PK = os.getenv("POLYGON_SOURCE_PK")

DEST_ADDRESS = os.getenv("BOT_WALLET_ADDRESS")
AMOUNT_MATIC = 370 # Leave 6 MATIC for gas in source

RPC = "https://polygon-rpc.com"

def execute_injection():
    print("WARNING: This will move REAL FUNDS on Polygon PoS.")
    
    if not SOURCE_PK:
        print("ERROR: POLYGON_SOURCE_PK not found in environment variables.")
        return

    if not DEST_ADDRESS:
        print("ERROR: BOT_WALLET_ADDRESS not found in environment variables.")
        return

    print(f"From: ...{SOURCE_PK[-6:]} (User Wallet)")
    print(f"To:   {DEST_ADDRESS} (Bot Wallet)")
    print(f"Amt:  {AMOUNT_MATIC} MATIC")
    
    confirm = input("Type 'EXECUTE' to confirm transaction: ")
    if confirm != "EXECUTE":
        print("Aborted.")
        return

    w3 = Web3(Web3.HTTPProvider(RPC))
    account = w3.eth.account.from_key(SOURCE_PK)
    
    # Build Tx
    nonce = w3.eth.get_transaction_count(account.address)
    gas_price = w3.eth.gas_price
    
    tx = {
        'nonce': nonce,
        'to': DEST_ADDRESS,
        'value': w3.to_wei(AMOUNT_MATIC, 'ether'),
        'gas': 21000,
        'gasPrice': gas_price,
        'chainId': 137
    }
    
    print("\n🚀 Signing Transaction...")
    signed_tx = w3.eth.account.sign_transaction(tx, SOURCE_PK)
    
    print("📡 Broadcasting...")
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    
    print(f"✅ SUCCESS! TX Hash: {w3.to_hex(tx_hash)}")
    print("Wait 30 seconds, then the bot will see the funds.")

if __name__ == "__main__":
    execute_injection()
