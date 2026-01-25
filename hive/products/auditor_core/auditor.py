import os
import re

import os
import re
import json

CONFIG_FILE = "auditor_config.json"

class TheAuditor:
    def __init__(self, target_dir="."):
        self.target_dir = target_dir
        self.findings = []
        self.load_config()

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            print(f"⚠️  CONFIG MISSING: {CONFIG_FILE}. Using defaults.")
            self.patterns = []
            self.ignore_dirs = [".git", "node_modules"]
            self.ignore_files = []
            return

        try:
            with open(CONFIG_FILE, 'r') as f:
                data = json.load(f)
                self.patterns = data.get("dangerous_patterns", [])
                self.ignore_dirs = data.get("ignore_dirs", [])
                self.ignore_files = data.get("ignore_files", [])
        except Exception as e:
            print(f"❌ CONFIG ERROR: {e}")
            self.patterns = []

    def scan(self):
        print(f"🕵️  THE AUDITOR: Scanning {os.path.abspath(self.target_dir)}...")
        
        for root, dirs, files in os.walk(self.target_dir):
            # Prune ignored directories
            dirs[:] = [d for d in dirs if d not in self.ignore_dirs]
            
            for file in files:
                if file in self.ignore_files: continue
                
                filepath = os.path.join(root, file)
                self.check_file(filepath)
                
        self.report()

    def check_file(self, filepath):
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            for i, line in enumerate(content.splitlines()):
                for p in self.patterns:
                    regex = p.get("regex")
                    name = p.get("name")
                    
                    if re.search(regex, line):
                        # Construct a "Finding"
                        self.findings.append({
                            "file": filepath,
                            "line": i + 1,
                            "type": name,
                            "snippet": line.strip()[:50] + "..." # Truncate for safety
                        })
        except Exception as e:
            # Skip binary files or weird encoding
            pass

    def report(self):
        print("\n" + "="*50)
        print(f"AUDIT COMPLETE: {len(self.findings)} Findings")
        print("="*50)
        
        if not self.findings:
            print("✅ CLEAN. No obvious secrets found.")
            return

        print("🚨 CRITICAL PATTERNS DETECTED:")
        for f in self.findings:
            print(f"  [FILE] {f['file']}")
            print(f"  [LINE] {f['line']}")
            print(f"  [TYPE] {f['type']}")
            print(f"  [CODE] {f['snippet']}")
            print("-" * 30)
            
        print("\nACTION: Review these files immediately. Rotate any confirmed keys.")

if __name__ == "__main__":
    bot = TheAuditor(".")
    bot.scan()
