"""
DEEP SCAN: Identify assets on ALL likely chains for BOTH wallets
ASCII ONLY
"""
from web3 import Web3

WALLETS = [
    "0x49F408664951b142b8cf955b2191f75737cE1960", # Bot Wallet
    "0x7aa67bFefb4FDafc779ff1843c6e3b3DfA0Af0a8"  # User Wallet
]

CHAINS = {
    "POLYGON_POS": {
        "rpc": "https://polygon-rpc.com",
        "tokens": {
            "USDC": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
            "USDC.e": "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
        }
    },
    "POLYGON_ZKEVM": {
        "rpc": "https://zkevm-rpc.com",
        "tokens": {
            "USDC": "0xA8CE8aee21bC2A48a5EF670afCc9274C7bbbC035",
            "USDC.e": "0x37e7D30CC184a7DAC4528434082F980eF12E811C"
        }
    },
    "ETHEREUM": {
        "rpc": "https://eth.llamarpc.com",
        "tokens": {
            "USDC": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
        }
    },
    "BASE": {
        "rpc": "https://mainnet.base.org",
        "tokens": {
            "USDC": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"
        }
    }
}

ERC20_ABI = [{"constant":True,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"balance","type":"uint256"}],"type":"function"}]

def scan():
    for wallet in WALLETS:
        print(f"\n{'='*40}")
        print(f"SCANNING WALLET: {wallet}")
        print(f"{'='*40}")
        
        for chain_name, data in CHAINS.items():
            print(f"  Checking {chain_name}...")
            try:
                w3 = Web3(Web3.HTTPProvider(data["rpc"], request_kwargs={'timeout': 5}))
                if not w3.is_connected():
                    print("    Failed to connect to RPC")
                    continue
                    
                # Check Native
                try:
                    eth = w3.eth.get_balance(wallet)
                    native_name = "MATIC" if "POS" in chain_name else "ETH"
                    val = w3.from_wei(eth, 'ether')
                    if val > 0.0001:
                        print(f"    FOUND Native {native_name}: {val:.5f}")
                except:
                    print("    Error checking native")
                
                # Check Tokens
                for name, addr in data["tokens"].items():
                    try:
                        addr = Web3.to_checksum_address(addr)
                        contract = w3.eth.contract(address=addr, abi=ERC20_ABI)
                        raw = contract.functions.balanceOf(wallet).call()
                        bal = raw / 10**6 # USDC is 6 dec
                        
                        if bal > 0.1: # Filter dust
                            print(f"    FOUND {name}: ${bal:,.2f}")
                    except:
                        pass # Silently skip errors to read output easier
                        
            except Exception as e:
                print(f"    Chain Error: {e}")

if __name__ == "__main__":
    scan()
