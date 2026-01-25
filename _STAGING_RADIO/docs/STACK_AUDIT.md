# GNU RADIO STACK AUDIT

*Vision: A sovereign, open-source radio infrastructure for the world's kids.*

## 1. The Core Stack (Validating "GNU/Open Status")

| Component | Current State | Open Source? | Verdict |
| :--- | :--- | :--- | :--- |
| **Logic** | Python 3.10 | ✅ YES (PSF License) | **SOLID** |
| **Brain** | Llama 3.2 (Ollama) | ✅ YES (Open Weights) | **SOLID** |
| **Interface** | HTML5/JS (PWA) | ✅ YES (Open Web Stds) | **SOLID** |
| **OS** | Windows 10 | ❌ NO (Proprietary) | **ACCEPTABLE (For now)**. The code is portable. Can run on Raspberry Pi (Linux). |
| **Hosting** | Firebase | ❌ NO (Google) | **RISK.** Free tier is generous, but it's not sovereign. |
| **Transport** | HTTPS/Web | ✅ YES | **SOLID** |

## 2. The Content Bottleneck (The "Live365" Issue)

**Current Status:** We are monitoring `andonlabs.com` (Proprietary Stream).
**The Issue:** If Andon Labs shuts down, FuzzRadio goes silent.
**The Fix:** We must inject **Public Domain** and **Creative Commons** audio.

### The GNU Library Roadmap

1. **Project Gutenberg / LibriVox:** For audiobooks (Education).
2. **Musopen / FreePD:** For CC0 Music.
3. **Local Generation:** Use `Magnet` or `MusicGen` (Meta Open Source) to generate our own "lofi" beats on the RTX 5070.

## 3. The "Yoto" Hardware Vision

* **Concept:** Low-power, rugged, offline-first.
* **FuzzRadio Bridge:**
  * **Phase 1:** Progressive Web App (PWA). Works on any cheap Android phone. Caches content for offline.
  * **Phase 2:** "Sneakernet" Update. The app can sync via local WiFi or even Bluetooth mesh (future) without high-bandwidth internet.

## 4. The Transformation

We are building a **Universal Educational Radio**.

* **Not just Music:** It creates "Curriculum" (The DJ Brain explains *why* the sky is blue between songs).
* **Cost:** $0 Content (Public Domain) + $0 Software (Open Source).
* **Hardware:** Runs on recycled smartphones.

*This stack is 90% there. The final 10% is swapping the audio source to local/public domain files.*
