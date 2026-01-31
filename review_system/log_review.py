import argparse
import json
import os
from datetime import datetime

JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reviews.json")


def log_review(url, name, summary, scores, recommendation, analysis):
    """Logs a review to the reviews.json file."""

    # Calculate weighted score (simple average for now, or use SME weights)
    # Weights: Strategic (1.5), Sovereign (1.5), Agentic (1.0), Tech (1.0)
    # Total possible: 15 + 15 + 10 + 10 = 50. Normalize to 100.
    w_strat = 1.5
    w_sov = 1.5
    w_agent = 1.0
    w_tech = 1.0

    raw_score = (
        (scores["strategic"] * w_strat)
        + (scores["sovereign"] * w_sov)
        + (scores["agentic"] * w_agent)
        + (scores["technical"] * w_tech)
    )

    max_score = (10 * w_strat) + (10 * w_sov) + (10 * w_agent) + (10 * w_tech)
    weighted_score = round((raw_score / max_score) * 100, 1)

    entry = {
        "timestamp": datetime.now().isoformat(),
        "url": url,
        "name": name,
        "summary": summary,
        "scores": scores,
        "weighted_score": weighted_score,
        "analysis": analysis,
        "recommendation": recommendation.upper(),
    }

    # Load existing
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE) as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(entry)

    with open(JSON_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Review logged for {name}. Score: {weighted_score}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Log a website review")
    parser.add_argument("--url", required=True)
    parser.add_argument("--name", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--strat", type=int, required=True, help="Strategic Fit (0-10)")
    parser.add_argument("--sov", type=int, required=True, help="Sovereign Compatibility (0-10)")
    parser.add_argument("--agent", type=int, required=True, help="Agentic Accessibility (0-10)")
    parser.add_argument("--tech", type=int, required=True, help="Technical Merit (0-10)")
    parser.add_argument(
        "--rec", required=True, choices=["INTEGRATE", "MONITOR", "IGNORE"], help="Recommendation"
    )
    parser.add_argument("--analysis", required=True, help="Detailed analysis text")

    args = parser.parse_args()

    scores = {
        "strategic": args.strat,
        "sovereign": args.sov,
        "agentic": args.agent,
        "technical": args.tech,
    }

    log_review(args.url, args.name, args.summary, scores, args.rec, args.analysis)
