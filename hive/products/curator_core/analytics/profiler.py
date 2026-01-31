
import json
import os
import re
from collections import Counter
from datetime import datetime

# PATHS
LOG_PATH = "dj_events.json"
REPORT_PATH = "../../../docs/reports/dj_analysis_profile.md"

def load_events():
    if not os.path.exists(LOG_PATH): return []
    with open(LOG_PATH) as f:
        return json.load(f)

def generate_profile():
    events = load_events()
    if not events:
        print("No DJ Events found.")
        return

    # 1. STATION BREAKDOWN
    stations = Counter(e['station'] for e in events)

    # 2. ENTITY EXTRACTION
    handles = []
    urls = []
    phone_numbers = []

    twitter_pattern = r'@[\w_]+'
    url_pattern = r'https?://\S+|www\.\S+'
    phone_pattern = r'\+?1?[-.]?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}'

    for e in events:
        text = f"{e['raw_title']} {e['raw_artist']}"
        handles.extend(re.findall(twitter_pattern, text))
        urls.extend(re.findall(url_pattern, text))
        phone_numbers.extend(re.findall(phone_pattern, text))

    # 3. HALLUCINATION DETECTION (Heuristic)
    # Looking for broken XML, code snippets, or extreme repetition
    hallucinations = [e for e in events if "{" in e['raw_title'] or "TypeError" in e['raw_title']]

    # 4. REPORT GENERATION
    report = f"""# 📡 DJ PSYCHO-PROFILE REPORT
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Events Analyzed:** {len(events)}

## 1. STATION ACTIVITY (Non-Music)
The heartbeat of the AI personalities.
"""
    for station, count in stations.items():
        report += f"* **{station}:** {count} Segments\n"

    report += f"""
## 2. DETECTED ENTITIES
**Twitter Handles:** {', '.join(set(handles)) if handles else "None detected"}
**Phone Numbers:** {', '.join(set(phone_numbers)) if phone_numbers else "None detected"}
**URLs Dropped:** {', '.join(set(urls)) if urls else "None detected"}

## 3. ANOMALY LOG (Hallucinations)
"""
    if hallucinations:
        for h in hallucinations:
            report += f"* ⚠️ [{h['station']}] {h['raw_title']}\n"
    else:
        report += "* ✅ No obvious model breakdowns detected.\n"

    report += """
## 4. PROGRAMMING RATIONALE
*Inferred topics based on segment titles.*
"""
    # Simple word cloud of topics
    # ...

    with open(REPORT_PATH, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"✅ Report generated at: {REPORT_PATH}")

if __name__ == "__main__":
    generate_profile()
