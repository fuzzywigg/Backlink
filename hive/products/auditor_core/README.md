# THE AUDITOR: Secret Scanner

**Version:** 1.0 (MVP)
**Type:** Compliance Tool (Stream #3)

## THE PROBLEM

Developers often commit secrets (Private Keys, API Keys) to code repositories. This causes catastrophic loss (e.g., the Jan 17 Incident).

## THE SOLUTION

A lightweight, fast Python script that scans your codebase for regex signatures of known secrets *before* you push.

## USAGE

1. Copy `auditor.py` to your project root.
2. Run `python auditor.py`.
3. Fix any red flags.

## SELLING POINT

"Don't lose $1,600 like we did. Run the check."
