"""
THE HUNTER: Death Zone Surveillance Daemon
------------------------------------------
Active monitoring of compromised assets and attacker movements.
Logs all events to 'war_room/evidence_locker.json'.

TARGETS:
1. 0x7aa... (Compromised Main)
2. 0x49F4... (Compromised Bot)
3. 0x1cc8... (CONFIRMED ATTACKER)

"""
import time
import json
import os
from datetime import datetime
from web3 import Web3

# --- CONFIGURATION ---
# --- CONFIGURATION ---
CONFIG_FILE = "hunter_config.json"

def load_config():
    """Loads configuration from external JSON file."""
    if not os.path.exists(CONFIG_FILE):
        print(f"⚠️  CONFIGURATION FILE MISSING: {CONFIG_FILE}")
        print("    Please create this file with 'rpc_url' and 'targets'.")
        return None
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ CONFIG LOAD ERROR: {e}")
        return None

def log_event(event_type, details, log_file):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": event_type,
        "details": details
    }
    
    # console output (Totalitarian Style)
    print(f"[{entry['timestamp']}] [ALERT] {event_type.upper()}: {details}")
    
    # File Append
    try:
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                data = json.load(f)
        else:
            data = []
        
        data.append(entry)
        
        with open(log_file, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"LOG ERROR: {e}")

    print("\n👁️  THE HUNTER IS ONLINE")
    print("-------------------------")
    
    config = load_config()
    if not config:
        return

    RPC_URL = config.get("rpc_url", "https://eth.llamarpc.com")
    TARGETS = config.get("targets", {})
    LOG_FILE = config.get("log_file", "evidence_locker.json")
    SCAN_INTERVAL = config.get("scan_interval", 15)

    if not TARGETS:
        print("❌ NO TARGETS CONFIGURED. Edit hunter_config.json.")
        return

    print(f"Monitored Targets: {len(TARGETS)}")
    print(f"Evidence Locker:   {LOG_FILE}")
    print("Connecting to Neural Link (RPC)...")
    
    try:
        w3 = Web3(Web3.HTTPProvider(RPC_URL))
        if not w3.is_connected():
            print("❌ LINK FAILURE. Check your RPC URL.")
            return
    except Exception as e:
        print(f"❌ CONNECTION ERROR: {e}")
        return

    print("✅ LINK ESTABLISHED. SURVEILLANCE ACTIVE.\n")
    
    # Baseline State
    state = {}
    for addr in TARGETS:
        try:
            checksum_addr = Web3.to_checksum_address(addr)
            state[checksum_addr] = {
                "balance": w3.eth.get_balance(checksum_addr),
                "nonce": w3.eth.get_transaction_count(checksum_addr)
            }
            name = TARGETS[addr]
            print(f"Locked on: {name}")
            print(f"  > Addr: {checksum_addr}")
            print(f"  > Bal:  {w3.from_wei(state[checksum_addr]['balance'], 'ether')} ETH")
            print(f"  > Tx:   {state[checksum_addr]['nonce']}")
        except Exception as e:
             print(f"⚠️  Target Error ({addr}): {e}")

    print("\n[...] SCANNING BLOCKS [...]")
    
    while True:
        try:
            for addr in TARGETS:
                checksum_addr = Web3.to_checksum_address(addr)
                if checksum_addr not in state: continue

                c_addr = checksum_addr
                name = TARGETS[addr]
                
                # 1. Check Balance
                new_bal = w3.eth.get_balance(c_addr)
                old_bal = state[c_addr]["balance"]
                
                if new_bal != old_bal:
                    diff = new_bal - old_bal
                    diff_eth = w3.from_wei(diff, 'ether')
                    msg = f"{name} Balance Change: {diff_eth:+.6f} ETH"
                    log_event("BALANCE_SHIFT", msg, LOG_FILE)
                    state[c_addr]["balance"] = new_bal
                    
                # 2. Check Nonce (Outgoing Tx)
                new_nonce = w3.eth.get_transaction_count(c_addr)
                old_nonce = state[c_addr]["nonce"]
                
                if new_nonce != old_nonce:
                    count = new_nonce - old_nonce
                    msg = f"{name} OUTGOING ACTIVITY DETECTED ({count} TXs)"
                    log_event("OUTGOING_TX", msg, LOG_FILE)
                    state[c_addr]["nonce"] = new_nonce

            time.sleep(SCAN_INTERVAL) # Approx 1 block time
            
        except KeyboardInterrupt:
            print("\n🛑 SURVEILLANCE TERMINATED.")
            break
        except Exception as e:
            print(f"⚠️ GLITCH: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run_hunter()
