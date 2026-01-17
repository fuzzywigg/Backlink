import os
import sys
from dotenv import load_dotenv
from web3 import Web3

# Force reload of .env
load_dotenv(override=True)

def verify_wallet_detailed():
    print("--- Detailed Wallet Balance Check ---")
    
    # 1. Check Env Var
    pk = os.getenv("POLYGON_SOURCE_PK")
    if not pk:
        print("❌ ERROR: POLYGON_SOURCE_PK not found.")
        return
    
    try:
        w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
        if not w3.is_connected():
            print("⚠️ WARNING: RPC Connection failed")
            return
            
        account = w3.eth.account.from_key(pk)
        address = account.address
        print(f"Address: {address}")
        
        # 3. Check Balance
        balance_wei = w3.eth.get_balance(address)
        balance_matic = w3.from_wei(balance_wei, 'ether')
        print(f"💰 Current Balance: {balance_matic} MATIC")
        print(f"💰 Current Balance (Wei): {balance_wei}")
        
        # Calculate Costs
        AMOUNT_TO_SEND = 370
        gas_price = w3.eth.gas_price
        gas_limit = 21000
        gas_cost_wei = gas_price * gas_limit
        total_cost_wei = w3.to_wei(AMOUNT_TO_SEND, 'ether') + gas_cost_wei
        
        print(f"\n--- Transaction Calculator ---")
        print(f"Amount to Send: {AMOUNT_TO_SEND} MATIC")
        print(f"Gas Price: {w3.from_wei(gas_price, 'gwei')} Gwei")
        print(f"Estimated Gas Cost: {w3.from_wei(gas_cost_wei, 'ether')} MATIC")
        print(f"Total Required: {w3.from_wei(total_cost_wei, 'ether')} MATIC")
        
        if balance_wei >= total_cost_wei:
            print("\n✅ Funds Sufficient")
        else:
            shortfall = w3.from_wei(total_cost_wei - balance_wei, 'ether')
            print(f"\n❌ INSUFFICIENT FUNDS. Short by {shortfall} MATIC")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_wallet_detailed()
