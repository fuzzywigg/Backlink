"""
PRIVATE KEY AUDIT: Direct check of the key provided
Checks derived address against known 0x49F4...
"""
from web3 import Web3

# The Key provided by user
PK = "0x6747f88678f0c7343974cef9e5a294421f31d339249bffa72fc39fa25161bf46"

# The Address we EXPECT (from .env and logs)
EXPECTED_ADDRESS = "0x49F408664951b142b8cf955b2191f75737cE1960"

def audit_key():
    print("🔐 PRIVACY AUDIT: Checking Key Derivation")
    
    try:
        w3 = Web3()
        account = w3.eth.account.from_key(PK)
        
        derived_address = account.address
        
        print("\n🔎 ANALYSIS:")
        print(f"  Input Key: {PK[:10]}...{PK[-6:]}")
        print(f"  Derived Address: {derived_address}")
        print(f"  Expected Address: {EXPECTED_ADDRESS}")
        
        if derived_address.lower() == EXPECTED_ADDRESS.lower():
            print("\n✅ MATCH CONFIRMED.")
            print("  This Private Key OWNS the Bot Wallet (0x49F4...)")
            print("  Conclusion: The bot has the correct key.")
        else:
            print("\n❌ MISMATCH DETECTED!")
            print("  This key does NOT belong to the bot wallet.")
            print("  Action: We must update .env with the correct key or address.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    audit_key()
