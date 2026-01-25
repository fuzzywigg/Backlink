import time
import json
import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
from web3 import Web3

# --- CONFIGURATION ---
CONFIG_FILE = "honeycomb_config.json"
DEFAULT_RPC = "https://eth.llamarpc.com"

class Honeycomb:
    def __init__(self):
        self.config = self.load_config()
        self.rpc_url = self.config.get("rpc_url", DEFAULT_RPC)
        self.baits = self.config.get("bait_wallets", [])
        self.alerts = self.config.get("alerts", {})
        self.state = {}
        
    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            print(f"Creating default config: {CONFIG_FILE}")
            # Default template
            dummy = {
                "rpc_url": "https://eth.llamarpc.com",
                "bait_wallets": [
                    {"address": "0xBAIT_WALLET_ADDRESS_HERE", "label": "Github Repo Decoy"}
                ],
                "alerts": {
                    "email_enabled": False,
                    "email_to": "you@example.com",
                    "email_smtp": "smtp.gmail.com",
                    "email_user": "alert_bot",
                    "email_pass": "secret"
                }
            }
            with open(CONFIG_FILE, 'w') as f:
                json.dump(dummy, f, indent=2)
            return dummy
            
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)

    def trigger_alert(self, msg):
        print("\n" + "!"*50)
        print(f"🚨 BREACH DETECTED: {msg}")
        print("!"*50 + "\n")
        
        # Log to disk (Critical Evidence)
        with open("BREACH_LOG.txt", "a") as f:
            f.write(f"[{datetime.utcnow()}] {msg}\n")
            
        # Optional: Email Alert (if configured)
        if self.alerts.get("email_enabled"):
            try:
                self.send_email(msg)
            except Exception as e:
                print(f"Failed to send email alert: {e}")

    def send_email(self, body):
        # Email logic placeholder - kept simple for MVP reliability
        pass

    def run(self):
        print(f"🐝 THE HONEYCOMB: Decoy Monitor Active")
        print(f"   Watching {len(self.baits)} Bait Wallets...")
        
        w3 = Web3(Web3.HTTPProvider(self.rpc_url))
        if not w3.is_connected():
            print("❌ RPC Connection Failed.")
            return

        # Initialize Baseline
        print("   Establishing Baseline...")
        for b in self.baits:
            addr = Web3.to_checksum_address(b["address"])
            self.state[addr] = {
                "balance": w3.eth.get_balance(addr),
                "nonce": w3.eth.get_transaction_count(addr),
                "label": b.get("label", "Unknown")
            }
            print(f"   [ARMED] {self.state[addr]['label']} ({addr[:8]}...)")

        print("   System Armed. Silent Mode Engaged.")

        # Loop
        while True:
            try:
                for addr, base in self.state.items():
                    # Check for ANY movement (Outgoing Tx or Balance Drop)
                    curr_nonce = w3.eth.get_transaction_count(addr)
                    curr_bal = w3.eth.get_balance(addr)
                    
                    if curr_nonce > base["nonce"]:
                        self.trigger_alert(f"OUTGOING TX detected on {base['label']}! (Nonce: {curr_nonce})")
                        base["nonce"] = curr_nonce # Reset to prevent spam
                        
                    if curr_bal < base["balance"]:
                        # Ignore tiny gas fluctuations, check significant drops
                        diff = base["balance"] - curr_bal
                        if diff > w3.to_wei(0.001, 'ether'): # Threshold
                            self.trigger_alert(f"BALANCE DRAIN detected on {base['label']}! -{w3.from_wei(diff, 'ether')} ETH")
                            base["balance"] = curr_bal

                time.sleep(15) 

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Loop Error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    bot = Honeycomb()
    bot.run()
