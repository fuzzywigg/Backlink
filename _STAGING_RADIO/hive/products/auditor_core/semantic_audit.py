# THE AUDITOR: Semantic Consistency Engine
# Uses the Local Beehive (Ollama) to check for stale documentation.

import os
import requests
import json
import glob

OLLAMA_API = "http://localhost:11434/api/generate"
MODEL = "qwen2.5-coder:7b" # Coding model is good for structured analysis

# The "Truth" - Hardcoded facts that must be reflected
FACTS = """
1. The "Hive" (Python Scripts) is Phase I (Legacy).
2. The "Sovereign Utility" (UHI) is Phase III/IV.
3. The Wallet "0x7aa..." is COMPROMISED/BURNED.
4. The Wallet "0x49F..." is COMPROMISED/BURNED.
5. "OpenAIR" is the primary broadcast station.
6. "Iron Dome" requires offline signing for ALL transactions.
"""

def check_file_semantics(filepath):
    """Asks the Local LLM if the file contradicts the Truth."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if len(content) > 4000: content = content[:4000] # Truncate for speed
        
        prompt = f"""
        You are a Documentation Auditor. Check the following file content against these FACTS:
        
        FACTS:
        {FACTS}
        
        FILE CONTENT:
        {content}
        
        TASK:
        Identify if this file contains OUTDATED information (e.g. references compromised wallets as safe, refers to old architectures as current).
        If it does, output "flag": true and a brief "reason".
        If it is consistent or historical, output "flag": false.
        
        Respond in JSON format: {{ "flag": boolean, "reason": "string" }}
        """
        
        response = requests.post(OLLAMA_API, json={
            "model": MODEL,
            "prompt": prompt,
            "format": "json",
            "stream": False
        })
        
        if response.status_code == 200:
            result = json.loads(response.json()['response'])
            return result
            
    except Exception as e:
        print(f"Error checking {filepath}: {e}")
        return None

def run_semantic_audit():
    print("🕵️  SEMANTIC AUDITOR: Checking Docs against The Truth...")
    
    # Path relative to hive/products/auditor_core/
    docs_dir = "../../../docs"
    # Verify path exists
    abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), docs_dir))
    if not os.path.exists(abs_path):
        print(f"❌ ERROR: Docs path not found at {abs_path}")
        return

    files = glob.glob(os.path.join(abs_path, "*.md"))
    print(f"   Found {len(files)} files to audit.")
    
    for f in files:
        print(f"   Checking {os.path.basename(f)}...")
        res = check_file_semantics(f)
        if res and res.get('flag'):
            print(f"   🚩 FLAGGED: {res['reason']}")
            issues.append({
                "file": f,
                "issue": res['reason']
            })
            
    # Save Report
    with open("semantic_audit_report.json", "w") as f:
        json.dump(issues, f, indent=2)
        
    print(f"✅ Audit Complete. {len(issues)} files flagged.")

if __name__ == "__main__":
    run_semantic_audit()
