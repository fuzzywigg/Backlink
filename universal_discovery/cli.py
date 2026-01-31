import os
import sys

# Ensure we can import local modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(current_dir))

from universal_discovery.engine import DiscoveryEngine


def interactive_wizard():
    engine = DiscoveryEngine()
    print(f"\n✨ Universal Discovery Wizard (Context: {engine.context_name.upper()}) ✨")
    print("---------------------------------------------------------------")

    # Step 1: Tool Selection
    print("Action:\n[1] New Discovery\n[2] Switch Context\n[3] Exit")
    choice = input("Select [1-3]: ").strip()

    if choice == "2":
        print("\nAvailable Contexts:")
        for ctx in engine.config["contexts"]:
            print(f"- {ctx}")
        new_ctx = input("Enter name: ").strip()
        if engine.set_context(new_ctx):
            print(f"✅ Switched to {new_ctx}")
        else:
            print("❌ Invalid context")
        return interactive_wizard()

    if choice == "3":
        sys.exit(0)

    # Step 2: The Input
    url = input("\n🔎 What did you find? (Paste URL): ").strip()
    if not url:
        return

    # Step 3: The Gap Analysis (ELI5)
    print("\n🧠 Thinking... (Checking Latent Context)")
    gap = engine.analyze_gap(url, "")
    print(f"💡 Insight: {gap['reason']}")

    # Step 4: User Input
    name = input("Name of Resource: ").strip()
    summary = input("Brief Summary: ").strip()

    print("\n📝 Quick Analysis:")
    analysis = input("Why is this useful? (Your notes): ").strip()

    # Step 5: Scoring (Simplified)
    print("\n📊 Scoring (0-10):")
    scores = {}
    if engine.context_name == "backlink_hive_scout":
        scores["strategic"] = int(input("Strategic Fit (0-10): ") or 0)
        scores["sovereign"] = int(input("Sovereign Compat (0-10): ") or 0)
        scores["agentic"] = int(input("Agentic Accessibility (0-10): ") or 0)
        scores["technical"] = int(input("Technical Merit (0-10): ") or 0)
    elif engine.context_name == "task_master":
        scores["Focus"] = int(input("Focus (0-10): ") or 0)
        scores["Depth"] = int(input("Depth (0-10): ") or 0)
        scores["Clarity"] = int(input("Clarity (0-10): ") or 0)
        scores["Utility"] = int(input("Utility (0-10): ") or 0)
    else:
        scores["Utility"] = int(input("Utility (0-10): ") or 5)
        scores["Quality"] = int(input("Quality (0-10): ") or 5)

    # Save
    entry = engine.save_review(url, name, summary, analysis, scores)
    print(f"\n✅ Saved to {engine.context['path']}")
    print(f"🏆 Score: {entry['weighted_score']}")


if __name__ == "__main__":
    try:
        interactive_wizard()
    except KeyboardInterrupt:
        print("\nGoodbye.")
