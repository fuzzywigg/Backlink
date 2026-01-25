import os
import time
import json
import glob
from datetime import datetime

# CONFIG
REFRESH_RATE = 5 # Seconds

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def load_json(path):
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except:
        return None
    return None

def get_hunter_status():
    # Reads evidence locker
    data = load_json("war_room/evidence_locker.json")
    if not data: return "Waiting for logs..."
    last_event = data[-1] if data else {}
    return f"Events Logged: {len(data)} | Last: {last_event.get('timestamp', 'N/A')} - {last_event.get('type', 'Unknown')}"

def get_honeycomb_status():
    # Reads aggregated library
    data = load_json("hive/honeycomb/aggregated_library.json")
    if not data: return "Waiting for data..."
    count = len(data)
    last_song = data[-1]['title'] if count > 0 else "None"
    return f"Library Size: {count} Songs | Latest: {last_song}"

def get_auditor_status():
    data = load_json("semantic_audit_report.json")
    if data is None: return "Not Run Yet"
    if len(data) == 0: return "✅ Last Scan Clean"
    return f"⚠️  {len(data)} Issues Found in Last Scan"

def get_iron_dome_status():
    # Counts proposal files
    proposals = glob.glob("hive/security/iron_dome/proposals/*.json")
    return f"📦 Pending Proposals: {len(proposals)}"

def draw_dashboard():
    while True:
        clear_screen()
        now = datetime.now().strftime("%H:%M:%S")
        
        print(f"""
  ____  _____ _____ _  _______ _____ _____  ______ _____  
 |  _ \| ____| ____| |/ / ____| ____|  __ \|  ____|  __ \ 
 | |_) | |__ | |__ | ' /| |__ | |__ | |__) | |__  | |__) |
 |  _ <|  __||  __||  < |  __||  __||  ___/|  __| |  _  / 
 | |_) | |___| |___| . \| |___| |___| |    | |____| | \ \ 
 |____/|_____|_____|_|\_\_____|_____|_|    |______|_|  \_\\
                                                          
  [ MISSION CONTROL ]                           {now}
  =======================================================
  
  👁️  THE WATCHTOWER (Hunter)
  -------------------------------------------------------
  STATUS: {get_hunter_status()}

  🐝  THE BEEHIVE (Memory/Curator)
  -------------------------------------------------------
  STATUS: {get_honeycomb_status()}

  🛡️  THE IRON DOME (Security)
  -------------------------------------------------------
  STATUS: {get_iron_dome_status()}
  AUDIT:  {get_auditor_status()}

  =======================================================
  [CTRL+C] to Exit Dashboard
        """)
        
        time.sleep(REFRESH_RATE)

if __name__ == "__main__":
    try:
        draw_dashboard()
    except KeyboardInterrupt:
        print("\nSee you space cowboy...")
