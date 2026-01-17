"""
ARRIVAL SCAN: Watch for 619 USDC landing on Ethereum Mainnet
"""
from web3 import Web3
import time

WALLET = "0x49F408664951b142b8cf955b2191f75737cE1960"

# Ethereum Mainnet
RPC = "https://eth.llamarpc.com"
USDC_ETH = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"

ERC20_ABI = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]

def check_arrival():
    print(f"📡 WATCHING ETHEREUM L1 for Arrival at {WALLET}...")
    
    try:
        w3 = Web3(Web3.HTTPProvider(RPC))
        contract = w3.eth.contract(address=USDC_ETH, abi=ERC20_ABI)
        
        # Check USDC Balance
        raw = contract.functions.balanceOf(WALLET).call()
        bal = raw / 10**6
        
        print(f"💰 CURRENT ETH L1 USDC: ${bal:,.2f}")
        
        if bal > 600:
            print("\n✅ FUNDS ARRIVED ON ETHEREUM!")
            print("Next Step: Bridge/Deposit from Eth L1 -> Polygon PoS")
        else:
            print("\n⏳ Still waiting... (Bridges can take 15-60 mins to finalize on L1)")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_arrival()
