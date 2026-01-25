import time
import json
import os
from datetime import datetime
from web3 import Web3

# --- CONSTANTS ---
CONFIG_FILE = "hunter_config.json"
DEFAULT_RPC = "https://eth.llamarpc.com"

class HunterCore:
    def __init__(self, config_path=CONFIG_FILE):
        self.config_path = config_path
        self.config = self.load_config()
        self.rpc_url = self.config.get("rpc_url", DEFAULT_RPC)
        self.targets = self.config.get("target_wallets", [])
        self.log_file = self.config.get("notifications", {}).get("log_file", "evidence_locker.json")
        self.state = {}
        
    def load_config(self):
        if not os.path.exists(self.config_path):
            print(f"[ERROR] Config file '{self.config_path}' not found.")
            print("Please create one using the template.")
            return {}
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load config: {e}")
            return {}

    def log_event(self, event_type, details, name):
        timestamp = datetime.utcnow().isoformat()
        entry = {
            "timestamp": timestamp, 
            "type": event_type, 
            "target": name,
            "details": details 
        }
        
        # Console Output
        print(f"[{timestamp}] [ALERT] {event_type} on {name}: {details}")
        
        # File Logging
        try:
            data = []
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = []
            
            data.append(entry)
            
            with open(self.log_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[LOG ERROR] Could not write to locker: {e}")

    def run(self):
        print(f"👁️ THE HUNTER: COMMERCIAL EDITION v1.0")
        print(f"   Mode: Active Surveillance")
        print(f"   Targets: {len(self.targets)}")
        print(f"   RPC: {self.rpc_url}")
        print("-" * 40)
        
        w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not w3.is_connected():
            print("❌ RPC CONNECTION FAILED")
            return

        # Initial State Capture
        print("Initializing Baseline...")
        for t in self.targets:
            addr = t.get("address")
            label = t.get("label", "Unknown")
            if not addr: continue
            
            clean_addr = Web3.to_checksum_address(addr)
            
            try:
                bal = w3.eth.get_balance(clean_addr)
                nonce = w3.eth.get_transaction_count(clean_addr)
                
                self.state[clean_addr] = {
                    "balance": bal,
                    "nonce": nonce,
                    "label": label
                }
                print(f"   [WATCHING] {label} ({clean_addr[:8]}...) - Bal: {w3.from_wei(bal, 'ether'):.4f} ETH")
            except Exception as e:
                print(f"   [ERROR] Could not init {label}: {e}")

        print("-" * 40)
        print("SYSTEM LIVE. MONITORING...\n")

        while True:
            try:
                for clean_addr, data in self.state.items():
                    # Check Balance
                    new_bal = w3.eth.get_balance(clean_addr)
                    if new_bal != data["balance"]:
                        diff = new_bal - data["balance"]
                        msg =f"Balance Change: {w3.from_wei(diff, 'ether'):.6f} ETH"
                        self.log_event("BALANCE", msg, data["label"])
                        self.state[clean_addr]["balance"] = new_bal
                    
                    # Check Tx Count (Nonce)
                    new_nonce = w3.eth.get_transaction_count(clean_addr)
                    if new_nonce != data["nonce"]:
                        msg = f"Transaction Broadcast Detected! (Nonce: {new_nonce})"
                        self.log_event("ACTIVITY", msg, data["label"])
                        self.state[clean_addr]["nonce"] = new_nonce
                
                time.sleep(15)
                
            except KeyboardInterrupt:
                print("\n[STOP] Surveillance Terminated by User.")
                break
            except Exception as e:
                print(f"[ERROR] Loop Exception: {e}")
                time.sleep(10)

if __name__ == "__main__":
    # Create a dummy config if none exists for testing
    if not os.path.exists(CONFIG_FILE):
        dummy = {
            "rpc_url": "https://eth.llamarpc.com",
            "target_wallets": [
                {"address": "0x7aa67bFefb4FDafc779ff1843c6e3b3DfA0Af0a8", "label": "DEMO_TARGET"}
            ]
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(dummy, f, indent=2)
            
    bot = HunterCore()
    bot.run()
