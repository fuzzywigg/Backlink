# Universal Discovery Protocol: Training Manual

## 1. The Concept: "One Tool, Many Contexts"

You often switch between "Building the Radio Station" (Sovereign, Hardcore Engineering) and "Just Browsing" (Cool ideas, random tools).

This tool adapts to you. It has three modes (Contexts):

1. **`backlink_hive_scout`**: Strict. Scores on Sovereignty, Agentic access, and Strategic fit. Saves to your official Hive Dashboard.
2. **`task_master`** (New): **Strict Agnostic**. Scores on "Focus", "Depth", and "Clarity". Doesn't care *what* the task is, but demands high quality execution relative to that task.
3. **`default`**: Relaxed. Scores on "Is this cool?" and "Is it useful?". Saves to a simple local file.

## 2. How to Use

### A. The "I found something cool" Workflow (CLI)

When you find a link and want to document it quickly without leaving your terminal:

1. **Run the Wizard**:

    ```powershell
    python universal_discovery/cli.py
    ```

2. **The AI Asks**: "What did you find?" -> Paste URL.
3. **The AI Checks**: It simulates checking your recent chat history to say "Hey, this fills that gap we talked about!".
4. **You Score**: Enter simple 0-10 numbers.
5. **Done**: It saves to the correct database automatically.

### B. The "Bunker" Workflow (Mobile/Remote)

When you are on your phone or away from the terminal:

1. **Open the Link**: `https://backlink-hive-123509617840.web.app/scout_input.html`
2. **Paste & Send**: That's it. It goes to the Hive Cloud.
3. **Inbox Processing**: When you get back to your computer, run:

    ```powershell
    python review_system/poll_inbox.py
    ```

    This pulls all your phone notes into the secure Hive Dashboard.

### C. Switching Contexts

If you want to start a completely new project (e.g., "Garden Monitor"):

1. Run `python universal_discovery/cli.py`
2. Select **[2] Switch Context**
3. Enter a new name. It will create a new profile for you.

## 3. Maintenance (Zero Bloat)

This tool is **self-contained**.

- **Files**: All logic is in `universal_discovery/`.
- **Data**: All data is in standard JSON files.
- **Uninstall**: Just delete the folder. Nothing installed in your Python site-packages except standard libraries (and `google-cloud-firestore` only if you use the Bunker features).
