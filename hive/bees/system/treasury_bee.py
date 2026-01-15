"""
Treasury Bee
------------
Responsible for the Hive's economic sovereignty.
Manages wallets, approves budgets, and executes x402 payments.
"""

from hive.bees.base_bee import BaseBee
from hive.utils.keys import KeyManager
import time

class TreasuryBee(BaseBee):
    """
    The Treasury Bee - Managing the Hive's sovereign finances.
    Implements x402 protocol standards for Agent-to-Agent payments.
    """
    
    def __init__(self, hive_path, gateway=None):
        super().__init__(hive_path, gateway)
        self.key_manager = KeyManager()
        # Try to get wallet key from environment or keys.json
        # Note: KeyManager usually checks os.getenv first, but we double check here
        # or load from the hidden .env file if KeyManager doesn't support it directly.
        self.wallet_key = self.key_manager.get_key("HIVE_WALLET_PRIVATE_KEY")
        
        # Fallback for dev environment if not set
        if not self.wallet_key:
             # Check if we can load it from .env manually (mvp hack)
             # In production, KeyManager should handle this transparently
             import os
             self.wallet_key = os.getenv("HIVE_WALLET_PRIVATE_KEY")

        if not self.wallet_key:
             self.log("WARNING: No Wallet Key found. Treasury operating in Read-Only mode.", level="warning")

    def work(self, task):
        """
        Execute treasury tasks.
        Supported instructions:
        - "check balance": Report current holdings.
        - "pay": Execute a payment (simulated for now).
        - "budget check": Verify if an expense is allowed.
        """
        instruction = task.get("instruction", "").lower()
        args = task.get("args", {})
        
        self.log(f"Processing treasury instruction: {instruction}")
        
        try:
            if "balance" in instruction:
                return self.check_balance()
            elif "pay" in instruction or "transfer" in instruction:
                return self.process_payment_request(args)
            elif "budget" in instruction:
                return self.approve_budget(args)
            else:
                 return {"success": False, "reason": f"Unknown treasury instruction: {instruction}"}
        except Exception as e:
            self.log(f"Treasury Error: {e}", level="error")
            return {"success": False, "error": str(e)}

    def check_balance(self):
        """
        Check wallet balances using Web3.
        Supports Polygon PoS, zkEVM, and Mainnet.
        """
        if not self.wallet_key:
             # Stub for MVP if no key
            balances = {
                "USDC": 619.20, # From user context (USDC Bridge task)
                "POL": 15.5,
                "ETH": 0.042
            }
            return {
                "success": True,
                "balances": balances,
                "msg": "Balance check simulated (Read-Only)."
            }

        try:
            from web3 import Web3
            from eth_account import Account
            
            account = Account.from_key(self.wallet_key)
            address = account.address
            
            # Check Polygon PoS (Target for daily ops)
            w3_poly = Web3(Web3.HTTPProvider("https://polygon-rpc.com"))
            balance_wei_poly = w3_poly.eth.get_balance(address)
            balance_pol = float(w3_poly.from_wei(balance_wei_poly, 'ether'))
            
            # Check Ethereum Mainnet (Savings)
            w3_eth = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))
            balance_wei_eth = w3_eth.eth.get_balance(address)
            balance_eth = float(w3_eth.from_wei(balance_wei_eth, 'ether'))

            # TODO: Add specific Token Contract checks (USDC, etc.)
            
            balances = {
                "POL": balance_pol,
                "ETH": balance_eth,
                "wallet": address
            }
            
            self.write_state({
                "treasury": {
                    "balances": balances,
                    "last_check": time.time(),
                    "wallet": address
                }
            })
            
            return {
                "success": True,
                "balances": balances,
                "msg": "Live balance check complete."
            }
            
        except Exception as e:
             self.log(f"Balance Check Failed: {e}", level="error")
             return {"success": False, "error": str(e)}
        
    def process_payment_request(self, args):
        """
        Execute an x402 payment (Agent Payments Protocol / AP2).
        Requires 'payment_request' dict compatible with AP2 standards.
        """
        amount = float(args.get("amount", 0))
        recipient = args.get("recipient", "0x000")
        reason = args.get("reason", "Service Payment")
        chain_id = args.get("chain_id", 137) # Default to Polygon PoS
        
        self.log(f"Request to pay {amount} USDC to {recipient} for '{reason}'")
        
        # 1. Budget Check
        if amount > 50.0: # Hardcoded safety limit
            self.log("Payment REJECTED: Exceeds auto-approval limit of $50", level="warning")
            return {"success": False, "reason": "Budget Exceeded (> 50 USDC)"}
        
        if not self.wallet_key:
            return {"success": False, "reason": "Read-Only Mode (No Key)"}

        try:
            # 2. Web3 Initialization
            from web3 import Web3
            from eth_account import Account
            
            # Setup RPC based on chain (Sovereign RPCs)
            rpc_urls = {
                137: "https://polygon-rpc.com", # Polygon PoS
                1101: "https://zkevm-rpc.com",   # Polygon zkEVM
                1: "https://eth.llamarpc.com",   # Mainnet
            }
            
            current_rpc = rpc_urls.get(chain_id, "https://polygon-rpc.com")
            w3 = Web3(Web3.HTTPProvider(current_rpc))
            
            # 3. Create Transaction
            account = Account.from_key(self.wallet_key)
            
            # Note: For strict AP2, we would sign a typed data structure (EIP-712).
            # For this MVP, we execute a direct transfer if it's a native token,
            # or interaction with a USDC contract if specified.
            # Assuming Native Token (POL/MATIC) for simple implementation first.
            
            # Current Nonce
            nonce = w3.eth.get_transaction_count(account.address)
            
            # Prepare Tx
            tx = {
                'nonce': nonce,
                'to': recipient,
                'value': w3.to_wei(amount, 'ether'), # Warning: Assumes Native Token amounts
                'gas': 21000,
                'gasPrice': w3.eth.gas_price,
                'chainId': chain_id
            }
            
            # 4. Sign and Send
            signed_tx = w3.eth.account.sign_transaction(tx, self.wallet_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
            
            tx_hex = w3.to_hex(tx_hash)
            self.log(f"Payment SENT: {tx_hex}", level="success")
            
            return {
                "success": True, 
                "tx_hash": tx_hex,
                "amount": amount,
                "recipient": recipient,
                "protocol": "ap2_native_transfer",
                "chain_id": chain_id
            }
            
        except Exception as e:
            self.log(f"Payment Failed: {e}", level="error")
            return {"success": False, "reason": str(e)}

    def approve_budget(self, args):
        """
        Pre-approval check for agents asking "Can I buy this?"
        """
        amount = float(args.get("estimated_cost", 0))
        item = args.get("item", "unknown")
        
        approved = amount <= 50.0
        return {
            "success": True,
            "approved": approved,
            "reason": "Within auto-approval limit" if approved else "Requires human sign-off"
        }
