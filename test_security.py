
import sys
import os
from pathlib import Path

# Add project root to path
current_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(current_dir))

from hive.bees.system.security_bee import SecurityBee

def test_security_bee():
    print("--- Security Bee Test ---")
    
    # 1. Create a dummy suspicious file
    dummy_apk_path = "suspicious_test_app.xml"
    with open(dummy_apk_path, "wb") as f:
        # Simulate binary manifest content with suspicious string
        f.write(b"PK\x03\x04\x00...")
        f.write(b"android.permission.RECORD_AUDIO")
        f.write(b"android.permission.READ_SMS")
        f.write(b"com.github.unidbg") # Trigger UniDBG detection too
        
    print(f"Created file: {dummy_apk_path}")
    
    # 2. Init Bee
    bee = SecurityBee(".")
    
    # 3. Test Manifest Scan
    print("\n[Test 1] Scanning Android Manifest...")
    res_manifest = bee.work({
        "instruction": "scan android manifest",
        "args": {"path": dummy_apk_path}
    })
    print(res_manifest)
    
    # 4. Test UniDBG Detection
    print("\n[Test 2] Detecting UniDBG...")
    res_unidbg = bee.work({
        "instruction": "detect unidbg signatures",
        "args": {"path": dummy_apk_path}
    })
    print(res_unidbg)
    
    # 5. Cleanup
    os.remove(dummy_apk_path)
    print("\nTest Complete (File removed).")

if __name__ == "__main__":
    test_security_bee()
