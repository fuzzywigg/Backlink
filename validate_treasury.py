
import sys
import os
from pathlib import Path
from web3 import Web3
from eth_account import Account

# Add project root to path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from hive.bees.system.treasury_bee import TreasuryBee
from hive.utils.keys import KeyManager

# ABIs
ERC20_ABI = [
    {"constant": True, "inputs": [{"name": "_owner", "type": "address"}], "name": "balanceOf", "outputs": [{"name": "balance", "type": "uint256"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
]

def check_token(w3, token_address, wallet_address, name):
    try:
        contract = w3.eth.contract(address=w3.to_checksum_address(token_address), abi=ERC20_ABI)
        balance = contract.functions.balanceOf(wallet_address).call()
        decimals = contract.functions.decimals().call()
        return float(balance) / (10 ** decimals)
    except Exception as e:
        return f"Error ({e})"

def validate():
    print("--- Treasury Validator & Deep Scan ---")
    
    km = KeyManager()
    
    # Define keys to check
    wallets = {
        "Primary (Polygon)": km.get_key("HIVE_WALLET_PRIVATE_KEY"),
        "Secondary (ETH)": km.get_key("HIVE_WALLET_PRIVATE_KEY_ETH")
    }
    
    for label, key in wallets.items():
        if not key:
            print(f"\nFAILURE: No Private Key found for {label}.")
            continue

        account = Account.from_key(key)
        address = account.address
        print(f"\n=== Target Wallet: {label} ===")
        print(f"Address: {address}")
        
        # 1. Ethereum Mainnet (Chain 1)
        print("[Scan] Ethereum Mainnet (Chain 1)")
        w3_eth = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))
        if w3_eth.is_connected():
            native = w3_eth.from_wei(w3_eth.eth.get_balance(address), 'ether')
            print(f"  > Native ETH:       {native}")
            # Check for USDC on Mainnet too, might vary
            usdc_mainnet = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
            print(f"  > USDC (Mainnet):   {check_token(w3_eth, usdc_mainnet, address, 'USDC')}")
        else:
            print("  > RPC Connection Failed")
    
        # 2. Polygon PoS (Chain 137)
        print("[Scan] Polygon PoS (Chain 137)")
        w3_poly = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
        if w3_poly.is_connected():
            native = w3_poly.from_wei(w3_poly.eth.get_balance(address), 'ether')
            print(f"  > Native MATIC/POL: {native}")
            
            # Contracts
            usdc_bridged = "0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174"
            usdc_native = "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359"
            weth_pos = "0x7ceB23fD6bC0adD59E62ac25578270cFf1b9f619"
            
            print(f"  > USDC.e (Bridged): {check_token(w3_poly, usdc_bridged, address, 'USDC.e')}")
            print(f"  > USDC (Native):    {check_token(w3_poly, usdc_native, address, 'USDC')}")
            print(f"  > WETH (Wrapped):   {check_token(w3_poly, weth_pos, address, 'WETH')}")
        else:
            print("  > RPC Connection Failed")
    
        # 3. Polygon zkEVM (Chain 1101)
        print("[Scan] Polygon zkEVM (Chain 1101)")
        w3_zkevm = Web3(Web3.HTTPProvider("https://zkevm-rpc.com"))
        if w3_zkevm.is_connected():
            native = w3_zkevm.from_wei(w3_zkevm.eth.get_balance(address), 'ether')
            print(f"  > Native ETH:       {native}")
            
            # USDC Check
            usdc_zkevm = "0xA8CE8aee21bC2A48a5EF670afCc9274C7bbbc035"
            print(f"  > USDC:             {check_token(w3_zkevm, usdc_zkevm, address, 'USDC')}")
        else:
            print("  > RPC Connection Failed")

if __name__ == "__main__":
    validate()
