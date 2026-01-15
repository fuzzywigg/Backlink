---
description: Universal Discovery Link Analysis
---

# Workflow: LinkHelp Analysis

Use this workflow when the user provides a URL and asks for help/analysis or uses `/linkhelp`.

## Steps

1. **Analyze Context**
   - Identify the user's current goal/task from `task.md` or recent conversation.
   - select the appropriate Rubric: `backlink_hive_scout`, `task_master`, or `default`.

2. **Read Content**
   - Use `read_url_content(url)` to fetch the page.

3. **Evaluate (Internal Monologue)**
   - **Gap Analysis**: Does this content solve a known problem?
   - **Scoring**: Rate 0-10 on the rubric dimensions.
     - *Backlink*: Strategic, Sovereign, Agentic, Technical.
     - *Task Master*: Focus, Depth, Clarity, Utility.
   - **Draft Analysis**: 1-2 sentences summarizing value.

4. **Verify with User (Optional)**
   - If unsure of relevance, ask the user: "This looks like a [Topic] resource. Should I log it to [Context]?"

5. **Save Record**
   - Use `run_command` to call the saver script:

   ```powershell
   python universal_discovery/save_record.py --url "[URL]" --name "[Title]" --summary "[Brief Summary]" --analysis "[Analysis]" --scores '{"Key": 8, "Key2": 9}' --context "[context_name]"
   ```

6. **Confirm**
   - Notify the user: "✅ Logged [Title] to [Context]. Score: [X]/10."
