# Backlink Hive: Website Evaluation Rubric

## Purpose

To systematically evaluate external websites, tools, and projects for integration into the Backlink Hive ecosystem.

## Evaluation Dimensions

### 1. Strategic Fit (Score 0-10)

*Is this useful for the Hive?*

- **10**: Critical Missing Piece (e.g., Solves a major blocker in Payment, Voice, or Memory).
- **7**: High Utility (e.g., Better content source, new revenue stream).
- **5**: Nice to have (e.g., UI polish, non-critical tool).
- **0**: Irrelevant.

### 2. Sovereign Compatibility (Score 0-10)

*Can we own this?*

- **10**: Fully Open Source / Self-Hostable (Docker/Local).
- **8**: Source Available / One-time Buy.
- **5**: SaaS but with Export/Sovereign Fallback.
- **0**: Black Box proprietary SaaS with lock-in.

### 3. Agentic Accessibility (Score 0-10)

*Can the Bees use this?*

- **10**: Official API or Structured Data (JSON/RSS).
- **7**: No API, but clean HTML/DOM for scraping.
- **3**: Heavy Client-Side JS / Obfuscated.
- **0**: Bot detections / Captchas / Walled Garden.

### 4. Technical Merit (Score 0-10)

*Is it good engineering?*

- **10**: Modern stack, active maintenance, good docs.
- **5**: Functional but aging or poorly documented.
- **0**: Deprecated, buggy, or insecure.

## Final Output Structure

Each review generates a JSON object:

```json
{
  "timestamp": "ISO8601",
  "url": "https://...",
  "name": "Site Name",
  "summary": "Brief description",
  "scores": {
    "strategic": 8,
    "sovereign": 10,
    "agentic": 5,
    "technical": 7
  },
  "weighted_score": 7.5,
  "analysis": "Detailed notes...",
  "recommendation": "INTEGRATE | MONITOR | IGNORE"
}
```
