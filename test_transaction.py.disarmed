
import sys
import time
from pathlib import Path
from web3 import Web3
from eth_account import Account

# Add project root to path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from hive.utils.keys import KeyManager

def execute_test_transfer():
    print("--- LIVE CRYPTO TRANSACTION TEST ---")
    
    # 1. Setup
    km = KeyManager()
    
    # Sender: Reserve Wallet (Has 376 POL)
    sender_key = km.get_key("HIVE_WALLET_PRIVATE_KEY_ETH")
    if not sender_key:
        print("Error: Reserve Key (HIVE_WALLET_PRIVATE_KEY_ETH) not found.")
        return

    # Recipient: Operating Wallet (Needs Gas)
    recipient_key = km.get_key("HIVE_WALLET_PRIVATE_KEY")
    if not recipient_key:
        print("Error: Operating Key (HIVE_WALLET_PRIVATE_KEY) not found.")
        return

    sender_account = Account.from_key(sender_key)
    recipient_account = Account.from_key(recipient_key)
    
    print(f"SENDER (Reserve):   {sender_account.address}")
    print(f"RECIPIENT (Op):     {recipient_account.address}")
    
    # 2. Connect to Polygon
    w3 = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
    if not w3.is_connected():
        print("Error: Could not connect to Polygon RPC")
        return
        
    chain_id = w3.eth.chain_id
    print(f"Connected to Polygon (Chain ID: {chain_id})")

    # 3. Check Balance
    balance_wei = w3.eth.get_balance(sender_account.address)
    balance_pol = w3.from_wei(balance_wei, 'ether')
    print(f"Sender Balance: {balance_pol} POL")
    
    amount_to_send = 0.01 # Very small test amount
    
    if balance_pol < amount_to_send:
        print("Insufficient funds for test.")
        return

    # 4. Construct Transaction
    print(f"\n प्रि Initiating Transfer of {amount_to_send} POL...")
    
    nonce = w3.eth.get_transaction_count(sender_account.address)
    gas_price = w3.eth.gas_price
    
    tx = {
        'nonce': nonce,
        'to': recipient_account.address,
        'value': w3.to_wei(amount_to_send, 'ether'),
        'gas': 21000,
        'gasPrice': gas_price,
        'chainId': chain_id
    }
    
    # 5. Sign & Send
    try:
        signed_tx = w3.eth.account.sign_transaction(tx, sender_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        print(f"✅ Transaction Sent!")
        print(f"Hash: {w3.to_hex(tx_hash)}")
        print(f"Tracking: https://polygonscan.com/tx/{w3.to_hex(tx_hash)}")
        
        print("\nWaiting for confirmation...")
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        if receipt.status == 1:
            print("🚀 SUCCESS: Transaction Confirmed on Blockchain.")
            print(f"Block Number: {receipt.blockNumber}")
            print(f"Gas Used: {receipt.gasUsed}")
        else:
            print("❌ FAILURE: Transaction Reverted.")
            
    except Exception as e:
        print(f"Transaction Failed: {e}")

if __name__ == "__main__":
    execute_test_transfer()
