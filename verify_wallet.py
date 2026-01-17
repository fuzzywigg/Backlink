import os
import sys
from dotenv import load_dotenv
from web3 import Web3

# Force reload of .env
load_dotenv(override=True)

def verify_wallet():
    print("--- Wallet Configuration Verification ---")
    
    # 1. Check Env Var
    pk = os.getenv("POLYGON_SOURCE_PK")
    if not pk:
        print("❌ ERROR: POLYGON_SOURCE_PK not found in environment variables.")
        print("Please ensure it is set in your .env file.")
        return
    
    print("✅ POLYGON_SOURCE_PK found in env.")

    try:
        # 2. Derive Address
        w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
        if not w3.is_connected():
            print("⚠️ WARNING: Could not connect to Polygon RPC. Checking offline derivation only.")
        
        account = w3.eth.account.from_key(pk)
        address = account.address
        print(f"✅ Derived Address: {address}")
        
        # 3. Check Balance
        if w3.is_connected():
            balance_wei = w3.eth.get_balance(address)
            balance_matic = w3.from_wei(balance_wei, 'ether')
            print(f"💰 Current Balance: {balance_matic: .4f} MATIC")
            
            # Check if sufficient for logic
            REQUIRED = 370
            if balance_matic < REQUIRED:
                 print(f"⚠️ WARNING: Balance ({balance_matic}) is less than the {REQUIRED} MATIC configured in inject_capital.py")
            else:
                 print(f"✅ Funds Sufficient: {balance_matic} > {REQUIRED}")
        
    except Exception as e:
        print(f"❌ Error verifying key/wallet: {e}")

if __name__ == "__main__":
    verify_wallet()
