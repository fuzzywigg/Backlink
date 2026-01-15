import sys
import os
import json
import requests
from bs4 import BeautifulSoup

# Ensure we can import local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from universal_discovery.engine import DiscoveryEngine

def run():
    engine = DiscoveryEngine()
    engine.set_context("backlink_hive_scout")
    
    pending = engine.get_pending_reviews()
    if not pending:
        print("No pending items.")
        return

    print(f"Processing {len(pending)} pending items...")

    for item in pending:
        url = item.get("url")
        print(f"\nProcessing: {url}")
        
        # Default Logic
        name = item.get("name")
        summary = item.get("summary")
        analysis = "Processed by Batch Agent."
        scores = {}
        status = "MONITOR"

        # 1. Claude Cookbooks (High Value)
        if "claude-cookbooks" in url or "platform.claude.com" in url:
            name = "Claude Cookbook Resource"
            summary = "Official Anthropics guide/notebook."
            if "orchestrator" in url:
                analysis = "CRITICAL: Orchestrator patterns are central to the Hive's 'Swarm' architecture."
                status = "INTEGRATE"
                scores = {"Strategic": 10, "Sovereign": 8, "Agentic": 10, "Technical": 9}
            elif "skills" in url:
                analysis = "Core reference for tool/skill definition, matching our Universal Discovery Protocol work."
                status = "INTEGRATE"
                scores = {"Strategic": 9, "Sovereign": 8, "Agentic": 10, "Technical": 8}
            elif "usage_cost" in url:
                analysis = "Utility for cost tracking. Monitoring only."
                status = "MONITOR"
                scores = {"Strategic": 5, "Sovereign": 5, "Agentic": 5, "Technical": 8}
            else:
                analysis = "General Claude resource. High value reference."
                status = "MONITOR"
                scores = {"Strategic": 7, "Sovereign": 7, "Agentic": 9, "Technical": 8}

        # 2. Google (Low Sovereignty)
        elif "google" in url:
            name = "Google Resource"
            summary = "Google documentation/console."
            analysis = "Low sovereignty, high utility. Keep on radar but do not integrate deeply."
            status = "IGNORE" if "console" in url else "MONITOR"
            scores = {"Strategic": 2, "Sovereign": 2, "Agentic": 5, "Technical": 8}

        # 3. SimonW (High Signal)
        elif "simonw" in url:
            name = "SimonW Resource"
            analysis = "Simon Willison is a key 'Sovereign AI' thought leader. His tools usually align perfectly with our ethos."
            status = "INTEGRATE"
            scores = {"Strategic": 9, "Sovereign": 10, "Agentic": 9, "Technical": 9}

        # 4. RLM (Unknown)
        elif "rlm" in url:
            name = "RLM (Unknown Repo)"
            analysis = "Needs manual review. Marked as Queued."
            status = "QUEUED"
            scores = {"Strategic": 5, "Sovereign": 5, "Agentic": 5, "Technical": 5}

        # 5. Dedupe Agents Standard
        elif "agents-standard" in url:
            print("Skipping agents-standard (duplicate)")
            # We can't delete easily via this API, but we can mark IGNORE
            status = "IGNORE"
            analysis = "Duplicate."
            scores = {"Strategic": 0, "Sovereign": 0, "Agentic": 0, "Technical": 0}

        # Save
        engine.save_review(
            url=url,
            name=name,
            summary=summary,
            analysis=analysis,
            rubric_scores=scores,
            update=True,
            recommendation=status
        )
        print(f" -> {status}")

if __name__ == "__main__":
    run()
