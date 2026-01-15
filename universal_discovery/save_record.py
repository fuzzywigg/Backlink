import argparse
import json
import os
import sys
import datetime

# Ensure we can import local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from universal_discovery.engine import DiscoveryEngine

def save_record(url, name, summary, analysis, scores_json, context_name, status_name=None):
    # Initialize Engine with specific context
    engine = DiscoveryEngine()
    
    if context_name:
        engine.set_context(context_name)
    
    scores = json.loads(scores_json)
    
    print(f"Saving review for {name} in context '{engine.context_name}'...")
    
    entry = engine.save_review(url, name, summary, analysis, scores, recommendation=status_name)
    
    print("SUCCESS")
    print(json.dumps(entry, indent=2))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--analysis", required=True)
    parser.add_argument("--scores", required=True, help="JSON string of scores")
    parser.add_argument("--context", help="Context to save in (default, backlink_hive_scout, task_master)")
    parser.add_argument("--status", help="Explicit status (INTEGRATE, MONITOR, IGNORE, REJECTED, QUEUED, GLOBAL)")
    
    args = parser.parse_args()
    
    save_record(args.url, args.name, args.summary, args.analysis, args.scores, args.context, args.status)
