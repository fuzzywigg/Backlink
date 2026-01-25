import os
import re
import sys

# DEEP SCAN: SECURITY AUDIT
# Scans the entire repository for potential secrets (Private Keys, API Keys)

SUSPICIOUS_PATTERNS = {
    "Private Key (Hex)": r"0x[a-fA-F0-9]{64}",
    "Private Key (Legacy)": r"-----BEGIN PRIVATE KEY-----",
    "OpenAI API Key": r"sk-[a-zA-Z0-9]{48}",
    "Generic API Key": r"[a-zA-Z0-9]{32,}", # Broad, might have false positives
    "Mnemonic Phrase": r"([a-z]{3,}\s){11}[a-z]{3,}" # 12 words
}

IGNORE_DIRS = {".git", ".venv", "__pycache__", "node_modules", ".pytest_cache", "site", "dist", "antigravity_evidence_package"}
IGNORE_FILES = {"package-lock.json", "poetry.lock", "yarn.lock", "deep_scan.py", "security_deep_scan.py", "models_cache.json", ".env.example"}

# Files known to contain example/compromised keys that we should ignore (or warn about contextually)
# We will list them here if they are "allowlisted" as safe examples.
ALLOWLIST_FILES = {
    "chainabuse_filing_data.txt", # Contains the compromised key for reporting
    "liability_admission.md", # Contains the compromised key for context
    "master_evidence_report.md",
    "commit_details.json",
    "incident_report.md",
    "forensic_report.md",
    "antigravity_evidence_package/chainabuse_filing_data.txt" # Duplicate path
}

def scan_file(filepath):
    """Scans a single file for secrets."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        found_issues = []
        for check_name, pattern in SUSPICIOUS_PATTERNS.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                # Basic context validation to reduce false positives (e.g. not in comments)
                # This is a simple scan, so we just report it.
                found_issues.append((check_name, match.group(0)[:10] + "..."))
        
        return found_issues
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return []

def run_deep_scan(root_dir):
    print(f"Starting Security Deep Scan on {root_dir}")
    print("=" * 60)
    
    issues_found = 0
    
    for root, dirs, files in os.walk(root_dir):
        # Prune ignored directories
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        
        for file in files:
            if file in IGNORE_FILES:
                continue
                
            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, root_dir)
            
            # Skip allowlisted files that document the incident
            if rel_path.replace("\\", "/") in ALLOWLIST_FILES or file in ALLOWLIST_FILES:
                continue
            
            # Check for high entropy file types? No, just scan text.
            issues = scan_file(filepath)
            
            if issues:
                for issue_type, preview in issues:
                    # Filter out the "Generic API Key" spam for now unless it looks very specific
                    if issue_type == "Generic API Key":
                        # Too noisy for now, skip unless very long and high entropy?
                        # Let's actually keep it off for this run to avoid spamming the user with hashes
                        continue
                        
                    print(f"[ALERT] {issue_type} found in: {rel_path}")
                    print(f"        Match: {preview}")
                    issues_found += 1

    print("=" * 60)
    if issues_found == 0:
        print("✅ DEEP SCAN COMPLETE. No new secrets found.")
    else:
        print(f"⚠️  DEEP SCAN COMPLETE. Found {issues_found} potential issues.")

if __name__ == "__main__":
    run_deep_scan(os.getcwd())
