import json
import os
import sys
import time
from datetime import datetime

# Setup paths
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REVIEWS_FILE = os.path.join(CURRENT_DIR, "reviews.json")
PROJECT_ID = "backlink-hive-123509617840"

try:
    from google.cloud import firestore
except ImportError:
    print(
        "Error: google-cloud-firestore not installed. Please run: pip install google-cloud-firestore"
    )
    sys.exit(1)


def load_reviews():
    if os.path.exists(REVIEWS_FILE):
        with open(REVIEWS_FILE) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_reviews(data):
    with open(REVIEWS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def poll_firestore():
    print(f"[{datetime.now().isoformat()}] Polling 'scout_inbox' for project {PROJECT_ID}...")

    try:
        # Client init (relies on ADC - Application Default Credentials)
        db = firestore.Client(project=PROJECT_ID)

        # Query PENDING
        inbox_ref = db.collection("scout_inbox")
        query = inbox_ref.where(filter=firestore.FieldFilter("status", "==", "PENDING"))
        docs = list(query.stream())

        if not docs:
            print("No pending submissions.")
            return

        reviews = load_reviews()
        new_count = 0

        for doc in docs:
            data = doc.to_dict()
            url = data.get("url")
            source = data.get("source", "unknown")
            data.get("timestamp")  # Firestore timestamp

            if not url:
                continue

            print(f"Received URL: {url} from {source}")

            # Create Pending Entry
            new_entry = {
                "timestamp": datetime.now().isoformat(),
                "url": url,
                "name": f"Inbox: {url.split('//')[-1].split('/')[0]}",  # Simple domain parse
                "summary": f"Received from {source}. Review pending.",
                "scores": {"strategic": 0, "sovereign": 0, "agentic": 0, "technical": 0},
                "weighted_score": 0.0,
                "analysis": "Received via remote inbox. Waiting for HITL review.",
                "recommendation": "PENDING",
            }

            # Prepend
            reviews.insert(0, new_entry)
            new_count += 1

            # Ack in Firestore
            doc.reference.update({"status": "RECEIVED", "received_at": firestore.SERVER_TIMESTAMP})

        if new_count > 0:
            save_reviews(reviews)
            print(f"Imported {new_count} new items to reviews.json")

    except Exception as e:
        print(f"Error polling Firestore: {e}")
        print("Tip: Run 'gcloud auth application-default login' if auth fails.")


if __name__ == "__main__":
    while True:
        poll_firestore()
        time.sleep(10)  # Poll every 10s
