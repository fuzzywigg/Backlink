import os
import secrets
from eth_account import Account
from pathlib import Path

def generate_and_save():
    env_path = Path(".env")
    
    # Generate
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    acct = Account.from_key(private_key)
    address = acct.address
    
    print(f"Generated New Bot Identity: {address}")
    
    # Read existing
    content = ""
    if env_path.exists():
        try:
            content = env_path.read_text(encoding="utf-8")
        except:
            pass # Create new if can't read
        
    # Append if not present
    if "BOT_WALLET_PRIVATE_KEY" in content:
        print("⚠️ BOT_WALLET_PRIVATE_KEY already exists in .env. Skipping generation to prevent overwrite.")
        return
        
    new_lines = f"\n\n# BOT WALLET (Generated Execution)\n"
    new_lines += f"BOT_WALLET_PRIVATE_KEY={private_key}\n"
    new_lines += f"BOT_WALLET_ADDRESS={address}\n"
    
    with open(env_path, "a", encoding="utf-8") as f:
        f.write(new_lines)
        
    print("✅ Credentials securely appended to .env")

if __name__ == "__main__":
    generate_and_save()
