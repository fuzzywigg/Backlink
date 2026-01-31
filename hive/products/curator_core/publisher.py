import datetime
import shutil
import subprocess
import time
from pathlib import Path

# --- CONFIGURATION ---
SOURCE_DB = Path("hive/honeycomb/aggregated_library.json")
PUBLIC_DB = Path("public/library.json")
DEPLOY_INTERVAL_SECONDS = 900  # 15 Minutes
# ---------------------

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}")

def deploy():
    log("🔄 Change detected. Preparing deployment...")

    # 1. Update Public File
    if not SOURCE_DB.exists():
        log("❌ Error: Source DB not found.")
        return

    shutil.copy(SOURCE_DB, PUBLIC_DB)
    log(f"✅ Copied library to {PUBLIC_DB}")

    # 2. Trigger Firebase Deploy
    # We use --only hosting to be fast
    try:
        log("🚀 Deploying to Firebase Hosting...")
        # Use shell=False for security - avoid shell injection
        subprocess.run(["firebase", "deploy", "--only", "hosting"], check=True, shell=False)
        log("✨ Deployment Complete. Site updated.")
    except subprocess.CalledProcessError as e:
        log(f"⚠️ Deployment Failed: {e}")
    except FileNotFoundError:
        log("⚠️ Firebase CLI not found. Install with: npm install -g firebase-tools")

def run_publisher():
    log("📡 Sovereign Publisher Online.")
    log(f"   Watching: {SOURCE_DB}")
    log(f"   Interval: {DEPLOY_INTERVAL_SECONDS}s")

    last_deploy_time = 0

    while True:
        try:
            # Check modification time
            if SOURCE_DB.exists():
                mtime = SOURCE_DB.stat().st_mtime

                # If modified SINCE last deploy
                if mtime > last_deploy_time:
                    # Optional: specific logic to wait for file close?
                    # For JSON, usually safe enough if we retry.

                    deploy()
                    last_deploy_time = time.time()
                else:
                    # No changes
                    pass

            time.sleep(DEPLOY_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            log("🛑 Publisher stopping.")
            break
        except Exception as e:
            log(f"⚠️ Error: {e}")
            time.sleep(60) # Backoff on error

if __name__ == "__main__":
    run_publisher()
