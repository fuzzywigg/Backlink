"""
VERIFY & PREP: Check if we can autonomously move the 376 MATIC
from User Wallet (0x7aa6...) to Bot Wallet (0x49F4...)
"""
from web3 import Web3

# User provided this key in chat history (Step 96)
SOURCE_PK = "f9e4680af162fdbddda4f35c0b4b88a2cce18aaab2530de2d567e1a41d6330d6"
SOURCE_EXPECTED = "0x7aa67bFefb4FDafc779ff1843c6e3b3DfA0Af0a8"

BOT_ADDRESS = "0x49F408664951b142b8cf955b2191f75737cE1960"

# Polygon PoS RPC
RPC = "https://polygon-rpc.com"

def check_viability():
    print("🕵️ CHECKING LIQUIDITY INJECTION PATH...")
    
    try:
        w3 = Web3(Web3.HTTPProvider(RPC))
        
        # 1. Verify Key Mappings
        account = w3.eth.account.from_key(SOURCE_PK)
        print(f"🔑 Source Key resolves to: {account.address}")
        
        if account.address.lower() != SOURCE_EXPECTED.lower():
            print("❌ Key mismatch! Cannot proceed autonomously.")
            return

        # 2. Check Balance
        bal_wei = w3.eth.get_balance(account.address)
        bal_matic = w3.from_wei(bal_wei, 'ether')
        
        print(f"💰 Balance on Polygon PoS: {bal_matic:.4f} MATIC")
        
        if bal_matic > 50:
            print("\n✅ VIABLE PATH FOUND:")
            print(f"   We can move {bal_matic - 2:.2f} MATIC from Source -> Bot ({BOT_ADDRESS})")
            print("   This will instantly fund the bot on the CORRECT CHAIN.")
        else:
            print("\n❌ Insufficient MATIC to fund operations.")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_viability()
