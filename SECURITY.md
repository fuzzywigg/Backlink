# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.1.x   | ✅ Active           |
| < 1.1   | ❌ End of life      |

## Reporting a Vulnerability

**Do NOT open a public GitHub issue for security vulnerabilities.**

### Private Disclosure

Report vulnerabilities privately via one of:

- **Email**: `andrew.pappas@nft2.me` (Andrew Pappas — Principal Architect)
- **GitHub Private Reporting**: Use [GitHub's private vulnerability reporting](https://github.com/fuzzywigg/Backlink/security/advisories/new)

### What to Include

1. Description of the vulnerability
2. Steps to reproduce (proof of concept if possible)
3. Affected component (bee name, module path, API endpoint)
4. Potential impact assessment
5. Suggested remediation (optional)

### Response SLA

| Severity | Acknowledgement | Resolution Target |
|----------|-----------------|-------------------|
| Critical | 24 hours        | 72 hours          |
| High     | 48 hours        | 7 days            |
| Medium   | 72 hours        | 30 days           |
| Low      | 1 week          | Next release      |

## Security Architecture

The hive implements several defense layers:

| Layer | Component | Description |
|-------|-----------|-------------|
| **Input Sanitization** | `hive/utils/safety.py` | Prompt injection detection, command whitelisting |
| **Constitutional Governance** | `constitutional_llm/src/constitutional_gateway.py` | Ethical action evaluation |
| **ML Classifier** | `hive/bees/defense/classifier_defense_bee.py` | Toxicity and jailbreak detection |
| **State Integrity** | `hive/utils/state_manager.py` | HMAC-SHA256 signed honeycomb state |
| **Path Traversal** | `hive/utils/storage_adapter.py` | Path sanitization for file operations |
| **Treasury Protection** | `hive/bees/system/treasury_bee.py` | Hardcoded wallet addresses, fraud detection |

## Known Security Considerations

- `HIVE_SECRET_KEY` must be set in production. A development fallback exists for `ENVIRONMENT=dev` only.
- Stripe webhook verification requires `STRIPE_WEBHOOK_SECRET` to be set; otherwise the system runs in simulation mode.
- The `ClassifierDefenseBee` falls back to regex patterns if the `transformers` library is unavailable.
- Iron Dome transaction proposals in `hive/security/iron_dome/proposals/` should not be committed to public repositories in production. Add this path to `.gitignore` before making the repo public, or ensure the proposals directory only contains sanitized/dummy data.

## Dependency Security

Dependencies are reviewed for CVEs. See `pyproject.toml` for version constraints.
Run `pip-audit` or `safety check` to audit installed packages.
