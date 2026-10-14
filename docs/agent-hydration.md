# Agent Hydration Report — fuzzywigg/Backlink

| Property      | Value                             |
|---------------|-----------------------------------|
| **Protocol**  | FUZZYWIGG Repo Hydration v1.0     |
| **Date**      | 2026-04-13                        |
| **Branch**    | `copilot/hydrate`                 |
| **Agent**     | copilot (GitHub Copilot)          |
| **Status**    | Phases 0-3 Complete; Phases 4-6 Delivered |
| **Edit Policy** | Agent-editable; structural changes require Andrew approval |

---

## Phase 1: Findings Report

### Identity

| Category | EXISTS | MISSING |
|----------|--------|---------|
| README | `README.md` (12 KB, comprehensive) | — |
| License | Declared MIT in `pyproject.toml` | `LICENSE` file (**now created**) |
| Package manifest | `pyproject.toml` (v1.1.0, setuptools) | — |
| Language/Framework | Python 3.10-3.12, FastAPI + Uvicorn | — |
| Purpose | AI autonomous radio station (swarm intelligence) | — |

### Source Architecture

| Category | EXISTS | MISSING |
|----------|--------|---------|
| Entry points | `hive/main_service.py` (FastAPI), `hive/queen/orchestrator.py` | — |
| Bee modules | 25 bees across 8 categories (~13,800 LOC) | `ScriptWriterBee`, `JingleBee`, `MusicDiscoveryBee`, `CompetitorWatchBee`, `SEOBee`, `ViralAnalystBee`, `NewsletterBee`, `MerchBee`, `VIPManagerBee` (all marked TODO) |
| State management | `hive/utils/state_manager.py` (HMAC-SHA256) | — |
| Intelligence | `hive/intelligence/dj_brain.py` (Ollama), `hive/utils/gemini_client.py` (Google) | — |
| Governance | `constitutional_llm/src/constitutional_gateway.py` | — |
| Defense | `hive/bees/defense/classifier_defense_bee.py` | — |

### Dependencies

| Category | EXISTS | MISSING |
|----------|--------|---------|
| Production | 22 deps in `pyproject.toml` | `stripe` library (commerce bee falls back to simulation), `supabase` client (storage gap), `transformers` (classifier bee optional) |
| Dev deps | pytest, mypy, ruff, black, isort, pre-commit | — |
| Lockfile | None | `pip-tools` lockfile (`requirements.lock`) |
| Docker | `Dockerfile` (python:3.11-slim), `docker-compose.sovereign.yaml` | — |

### Tests

| Category | EXISTS | MISSING |
|----------|--------|---------|
| Framework | pytest + pytest-asyncio + pytest-mock + pytest-cov | — |
| Test files | 13 in `tests/`, 8 in `hive/tests/` (~3,094 LOC) | — |
| Coverage threshold | 60% minimum (`pyproject.toml`) | — |
| Untested modules | — | `hive/main_service.py` (FastAPI endpoints), `hive/queen/orchestrator.py`, `constitutional_llm/src/constitutional_gateway.py`, `hive/utils/payment_processor.py` |
| Test markers | `unit`, `integration`, `slow` | No `conftest.py` in `hive/tests/` |

### CI/CD

| Category | EXISTS | MISSING |
|----------|--------|---------|
| Lint | Ruff (blocking) | — |
| Type check | mypy (`continue-on-error: true` ⚠️) | Should be blocking |
| Test | 3-way matrix (3.10/3.11/3.12), Codecov upload | — |
| Security | Bandit (`continue-on-error: true` ⚠️) | Should be blocking; no CodeQL |
| Build | `python -m build` + twine check | — |
| Deployment | `deploy_godaddy.yml` (docs), `deploy_docs.yml` (GH Pages), `deploy-cloudflare-pages.yml` (CF Pages), `deploy-cloud-run.yml` (Cloud Run, `workflow_dispatch`, no auto-promote; WIF vars live as of run `35880833596`) | Merge ≠ deploy; promote remains intentional HITL |
| Dependency updates | None | `dependabot.yml` (**now created**) |

### Documentation

| Category | EXISTS | MISSING |
|----------|--------|---------|
| README | ✅ Rich, 12 KB | — |
| CLAUDE.md | ✅ Comprehensive | — |
| Agent.md | ✅ Full DJ instruction file (20 KB) | — |
| SWARM_ROLES.md | ✅ `hive/SWARM_ROLES.md` | — |
| GAP_ANALYSIS | ✅ `docs/GAP_ANALYSIS_REPORT.md` | — |
| Changelog | ❌ | `CHANGELOG.md` |
| API docs | mkdocs partial | Auto-generated API reference |
| Agent hydration | ❌ | `docs/agent-hydration.md` (**this file**) |

### Governance

| Category | EXISTS | MISSING |
|----------|--------|---------|
| CLAUDE.md | ✅ `CLAUDE.md` | — |
| CONTRIBUTING.md | ✅ `CONTRIBUTING.md` | — |
| SECURITY.md | ✅ `SECURITY.md` | — |
| LICENSE | ✅ `LICENSE` | — |
| CODEOWNERS | ❌ | `.github/CODEOWNERS` |
| PR Template | ✅ `.github/pull_request_template.md` | — |
| AGENTS.md | ✅ `docs/lore/AGENTS.md` | — |

### Security

| Category | EXISTS | MISSING |
|----------|--------|---------|
| Secret handling | `.gitignore`, `.env.example`, HMAC signing | `.secrets.baseline` (still absent; pre-commit references it), SECURITY.md (**now created**) |
| Input validation | `safety.py`, `constitutional_gateway.py`, `classifier_defense_bee.py` | — |
| Stripe webhook HMAC | `payment_processor.py` (simulation mode without key) | `stripe` library in `pyproject.toml` |
| CodeQL | ❌ | `.github/workflows/codeql.yml` |
| Path traversal | ✅ `storage_adapter.py` checks prefix | — |

### Observability

| Category | EXISTS | MISSING |
|----------|--------|---------|
| Structured logging | `hive/utils/logging.py`, per-bee loggers | JSON-format logs for Cloud Run |
| Health endpoint | `/health` in `main_service.py` | Health endpoint tests |
| Analytics | `hive/utils/plausible_andon.py` | Prometheus/OpenTelemetry metrics |
| Alerting | Bee failure tracker in orchestrator | No external alerting (PagerDuty, Slack) |

---

## Phase 2: Questions

### LIST A — Resolved by Research

| Question | Answer | Source |
|----------|--------|--------|
| Does a LICENSE file exist? | Yes — `LICENSE` at repo root (MIT) | File system |
| Is there a SECURITY.md? | Yes — `SECURITY.md` at repo root | File system |
| Is Bandit CI blocking? | No — `continue-on-error: true` | `.github/workflows/ci.yml:96` |
| Is mypy CI blocking? | No — `continue-on-error: true` | `.github/workflows/ci.yml:36` |
| Is stripe in deps? | No — optional import only | `pyproject.toml`, `payment_processor.py:7` |
| Does .secrets.baseline exist? | No — pre-commit hook references it | File system |
| Does dependabot.yml exist? | Yes — `.github/dependabot.yml` | File system |
| Is there a Cloud Run deploy workflow? | Yes — `deploy-cloud-run.yml` (manual dispatch; dry_run default; no auto-promote). WIF vars live (first real deploy run `35880833596` → revision `backlink-hive-00014-xej` / tag `tip-e5271783e763`). CF Pages / GoDaddy / docs deploys remain separate. | `.github/workflows/deploy-cloud-run.yml`, `cloudbuild.provenance.yaml`, `docs/DEPLOYMENT_HANDOFF.md` |
| Is there a PR template? | Yes — `.github/pull_request_template.md` | File system |
| Is Live365 streaming implemented? | No — DjBee simulates it | `docs/GAP_ANALYSIS_REPORT.md`, `hive/bees/content/dj_bee.py` |
| Is Supabase implemented? | No — FILE + FIRESTORE only | `hive/utils/storage_adapter.py` |
| Does orchestrator.py have tests? | No | `tests/` and `hive/tests/` scans |
| Does main_service.py have tests? | No | `tests/` scan |

### LIST B — Requires Andrew (HITL)

These cannot be resolved from the codebase alone:

1. **PikoClaw demo at Panathenea (May 27-29, 2026)**: Which specific features must be live and demo-ready? This gates P1 priority assignments.
2. **Payment processor priority**: Is Stripe the confirmed P1 payment path, or is Lightning Network (ETH/SOL) via Iron Dome the priority?
3. **Live365 encoder credentials**: Is there an active Live365 account and station ID? Without this, DjBee cannot move from simulation to production audio.
4. **Supabase instance**: Is there a Supabase project provisioned? What is the URL and key structure?
5. **Cloud Run redeployment**: ~~auto on `main`?~~ **Resolved for v1:** manual `workflow_dispatch` only (`deploy-cloud-run.yml`), `dry_run` default true, `promote` default false. WIF/vars live; promote / traffic shift remains intentional HITL.
6. **Branch protection rules on `main`**: Should mypy and Bandit be enforced as hard blockers before merge?

---

## Phase 4: Prepared Issues

> **Note**: GitHub issue creation requires authentication (HITL). Copy each block below into the GitHub Issues UI or use `gh issue create`.
> Issue title format: `[surface] Title`

---

### PHASE 1 ISSUES (Foundation — P1)

---

#### Issue 1: [copilot] Add LICENSE file (MIT)

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: copilot
Source links: pyproject.toml (license = {text = "MIT"})
Edit policy: Agent-editable

**Problem**
`pyproject.toml` declares `license = {text = "MIT"}` but no `LICENSE` file exists in the repository root.
GitHub cannot detect the license without this file, affecting discoverability and legal compliance.

**Proposed Solution**
Add standard MIT `LICENSE` file with copyright holder set to "Andon Labs / fuzzywigg.ai".
File path: `LICENSE`

**Acceptance Criteria**
- [ ] `LICENSE` file exists at repo root
- [ ] GitHub correctly detects "MIT License" in repository metadata
- [ ] Copyright year and holder are accurate

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | copilot |
| Rationale | Single-file creation, no logic required |
| Priority | P1 — Legal compliance, unblocks partnership/investor relations |
| Branch | `copilot/add-license` |
| Dependencies | None |
```

---

#### Issue 2: [copilot] Add SECURITY.md vulnerability disclosure policy

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: copilot
Source links: GitHub security best practices, docs/lore/AGENTS.md (authority hierarchy)
Edit policy: Agent-editable; contact info requires Andrew approval

**Problem**
No `SECURITY.md` exists. GitHub displays a warning and external researchers have no documented
path to report vulnerabilities privately. The hive processes payments and crypto transactions,
making this a critical gap.

**Proposed Solution**
Create `SECURITY.md` at repo root following GitHub's standard format:
- Supported versions table
- Private disclosure email (andrew.pappas@nft2.me)
- Response SLA by severity
- Overview of security architecture (safety.py, constitutional_gateway.py, etc.)

**Acceptance Criteria**
- [ ] `SECURITY.md` exists at repo root
- [ ] GitHub "Security" tab shows the policy
- [ ] Private advisory reporting URL is included
- [ ] Security architecture components are listed

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | copilot |
| Rationale | Documentation creation, no code changes |
| Priority | P1 — Security posture, required for any production deployment |
| Branch | `copilot/add-security-policy` |
| Dependencies | None |
```

---

#### Issue 3: [copilot] Fix CI: make Bandit and mypy blocking

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: copilot
Source links: .github/workflows/ci.yml:36 (mypy), .github/workflows/ci.yml:96 (bandit)
Edit policy: Agent-editable

**Problem**
Both `mypy` type checking and `bandit` security scanning use `continue-on-error: true` in CI.
This means PRs can merge with type errors and security vulnerabilities without any gate.
The hive manages crypto transactions and LLM inputs — security failures must block merges.

**Proposed Solution**
1. Remove `continue-on-error: true` from the `mypy` step in `ci.yml`
2. Remove `continue-on-error: true` from the `bandit` step in `ci.yml`
3. Fix any existing mypy/bandit failures that would now block CI

**Acceptance Criteria**
- [ ] `ci.yml` has no `continue-on-error: true` on mypy or bandit steps
- [ ] CI pipeline fails (red) when mypy errors are present
- [ ] CI pipeline fails (red) when bandit finds HIGH/MEDIUM severity issues
- [ ] All current mypy and bandit errors are resolved or explicitly suppressed with justification

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | geryon |
| Rationale | Requires fixing type errors across the codebase, multi-file changes |
| Priority | P1 — Security enforcement gate |
| Branch | `geryon/enforce-ci-security-gates` |
| Dependencies | None |
```

---

#### Issue 4: [copilot] Add .github/dependabot.yml for automated dependency updates

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: copilot
Source links: pyproject.toml (22 production deps), .github/ contents
Edit policy: Agent-editable

**Problem**
No `dependabot.yml` exists. Security dependencies (`cryptography`, `urllib3`, `certifi`) were
manually updated on 2026-01-31 (per comment in pyproject.toml), indicating no automated process.
Without Dependabot, CVEs in transitive dependencies will go undetected.

**Proposed Solution**
Create `.github/dependabot.yml` with:
- Weekly pip updates, grouped security updates
- Weekly GitHub Actions updates
- Ignore major version bumps for `cognee` (unstable API)

**Acceptance Criteria**
- [ ] `.github/dependabot.yml` exists and is valid YAML
- [ ] Dependabot PRs appear in the repository within 1 week
- [ ] Security group (`cryptography`, `urllib3`, etc.) is configured
- [ ] GitHub Actions ecosystem is included

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | copilot |
| Rationale | Config-only change, no code logic |
| Priority | P1 — Continuous security patch automation |
| Branch | `copilot/add-dependabot` |
| Dependencies | None |
```

---

#### Issue 5: [copilot] Generate .secrets.baseline for detect-secrets pre-commit hook

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: copilot
Source links: .pre-commit-config.yaml (detect-secrets hook)
Edit policy: Agent-editable

**Problem**
`.pre-commit-config.yaml` includes the `detect-secrets` hook with `--baseline .secrets.baseline`,
but no `.secrets.baseline` file exists. Running `pre-commit run --all-files` fails immediately
with a missing baseline error, blocking all contributors from using pre-commit hooks.

**Proposed Solution**
Run `detect-secrets scan --exclude-files <large-json-files> > .secrets.baseline` and commit the result.
Exclude: `beehive_index.json`, `models_cache.json`, iron dome proposal JSONs, docs API JSON.

**Acceptance Criteria**
- [ ] `.secrets.baseline` exists at repo root
- [ ] `pre-commit run detect-secrets --all-files` passes
- [ ] No actual secrets are in the baseline (only false-positive tokens)

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | copilot |
| Rationale | Single command + commit |
| Priority | P1 — Unblocks all contributor pre-commit workflows |
| Branch | `copilot/add-secrets-baseline` |
| Dependencies | None |
```

---

### PHASE 2 ISSUES (Hardening — P2)

---

#### Issue 6: [copilot] Add .github/CODEOWNERS file

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: copilot
Source links: docs/lore/AGENTS.md (authority hierarchy: mr_pappas, fuzzywigg, nft2me)
Edit policy: Agent-editable; ownership assignments require Andrew approval

**Problem**
No CODEOWNERS file. Merges to sensitive paths (treasury, constitutional_llm, security) have no
auto-review requirements. This is especially critical for the Iron Dome and payment flows.

**Proposed Solution**
Create `.github/CODEOWNERS`:
- `*` → @fuzzywigg (all files)
- `hive/security/` → @fuzzywigg
- `constitutional_llm/` → @fuzzywigg
- `hive/bees/system/treasury_bee.py` → @fuzzywigg
- `hive/utils/payment_processor.py` → @fuzzywigg
- `.github/` → @fuzzywigg

**Acceptance Criteria**
- [ ] `.github/CODEOWNERS` is valid
- [ ] PRs touching treasury/security files auto-request @fuzzywigg review
- [ ] GitHub shows "Changes approved" requirement for protected paths

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | copilot |
| Rationale | Config-only, but ownership requires human confirmation |
| Priority | P2 — Security governance enforcement |
| Branch | `copilot/add-codeowners` |
| Dependencies | Issue #1 (LICENSE) |
```

---

#### Issue 7: [copilot] Add .github/workflows/codeql.yml security scanning

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: copilot
Source links: .github/workflows/ (no CodeQL), pyproject.toml (Python project)
Edit policy: Agent-editable

**Problem**
No CodeQL workflow exists. Bandit covers Python security linting but misses semantic
vulnerabilities (path traversal, injection patterns, insecure deserialization) that CodeQL
detects via data-flow analysis. The hive handles LLM inputs, payment webhooks, and crypto
transactions — high-value targets requiring deep SAST.

**Proposed Solution**
Add `.github/workflows/codeql.yml`:
- Triggers: push to main, PRs, weekly schedule
- Language: python
- Queries: security-extended
- Upload results to GitHub Security tab

**Acceptance Criteria**
- [ ] `.github/workflows/codeql.yml` is valid and runs successfully
- [ ] CodeQL results appear in GitHub Security > Code scanning alerts
- [ ] No HIGH/CRITICAL findings are unaddressed
- [ ] Weekly scheduled scan runs

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | copilot |
| Rationale | YAML workflow creation, no Python changes |
| Priority | P2 — Deep SAST coverage |
| Branch | `copilot/add-codeql` |
| Dependencies | None |
```

---

#### Issue 8: [geryon] Add Cloud Run deployment workflow

```
Status: PARTIAL — Path B workflow + first live deploy landed; promote discipline / tip-vs-main lag still operator HITL
Tier: 1
Created: 2026-04-13
Owner: geryon
Source links: README.md, Dockerfile, docs/DEPLOYMENT_HANDOFF.md,
  .github/workflows/deploy-cloud-run.yml, cloudbuild.provenance.yaml, issue #89 / PR #90
Edit policy: Agent-editable workflow/docs; do not change WIF/IAM/secrets or force traffic
  from agents without explicit HITL. Do NOT commit JSON service-account keys.

**Problem**
`Dockerfile` and Cloud Run are the production target, but historically only a manual Andon CLI
sketch existed in `docs/DEPLOYMENT_HANDOFF.md`. Auto push-to-main deploy is intentionally out of
scope for v1 (traffic safety).

**Implemented (Path B)**
- `.github/workflows/deploy-cloud-run.yml` — `workflow_dispatch` with `dry_run` (default true) and
  `promote` (default false); WIF via `google-github-actions/auth`; Cloud Build via
  `cloudbuild.provenance.yaml`; deploy by digest with `--no-traffic`;
  `--update-env-vars` only for `GIT_SHA,BUILD_ID,BUILD_TIMESTAMP`; `/health` git_sha verify;
  promote job gated separately.
- Docs updated so the CLI sketch is no longer the only truth.

**Remaining HITL**
- [x] WIF + GitHub vars live (Path B real deploy succeeded: Actions run `35880833596`)
- [x] First real run: `dry_run=false`, `promote=false`; tagged `/health` OK on
      `tip-e5271783e763` / revision `backlink-hive-00014-xej`
- [ ] Keep promote intentional (`promote=true` or explicit HITL traffic shift); do not
      assume merge redeploys. Serving tip as of 2026-09-26 matches `00014-xej` provenance
      on the default URL (handoff-era `00011-mrt` @ tag `tip` superseded).
- [ ] Rollback reference: `backlink-hive-00010-pr9`

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | geryon |
| Rationale | Multi-step GCP workflow with WIF (no SA JSON keys) |
| Priority | P2 — CI path exists; IAM still HITL |
| Branch | `cursor/cloud-run-ci-deploy-af4d` |
| Dependencies | Issue #89 / PR #90 (`/health` provenance) |
```

---

#### Issue 9: [copilot] Add stripe to pyproject.toml optional dependencies

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: copilot
Source links: hive/utils/payment_processor.py:7, docs/GAP_ANALYSIS_REPORT.md §2.1, hive/schemas/payment.py
Edit policy: Agent-editable

**Problem**
`payment_processor.py` does `try: import stripe except ImportError: stripe = None` and silently
falls back to simulation mode. The `stripe` library is not in any `pyproject.toml` dep group.
The `/webhook` endpoint in `main_service.py` will silently fail to verify Stripe signatures in
production without this library, creating a security gap.

**Proposed Solution**
1. Add `stripe>=6.0.0` to `[project.optional-dependencies].payment` group in `pyproject.toml`
2. Add `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` to `.env.example`
3. Add startup warning to `main_service.py` if stripe is not installed and `STRIPE_SECRET_KEY` is set
4. Update `INSTALL.md` or README with `pip install -e ".[payment]"` instructions

**Acceptance Criteria**
- [ ] `stripe` appears in `pyproject.toml` optional deps
- [ ] `pip install -e ".[payment]"` installs stripe
- [ ] `STRIPE_SECRET_KEY` and `STRIPE_WEBHOOK_SECRET` in `.env.example`
- [ ] Startup log warns if stripe is not available but key is configured

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | copilot |
| Rationale | Dependency + env template update, no logic changes |
| Priority | P2 — Payment security gap |
| Branch | `copilot/add-stripe-dependency` |
| Dependencies | None (HITL: Stripe credentials from Andrew) |
```

---

#### Issue 10: [geryon] Add Supabase backend to StorageAdapter

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: geryon
Source links: docs/GAP_ANALYSIS_REPORT.md §2.3, hive/utils/storage_adapter.py
Edit policy: Agent-editable

**Problem**
`StorageAdapter` supports `FILE` and `FIRESTORE` backends only. Large media assets (audio files,
clips) cannot be reliably stored or retrieved. The gap analysis documents this as critical for
end-to-end functionality. `ClipCutterBee` and `DjBee` are blocked from producing real audio output.

**Proposed Solution**
Add `SUPABASE` storage backend to `StorageAdapter`:
1. Add `supabase>=2.0.0` to optional deps in `pyproject.toml` (`[project.optional-dependencies].storage`)
2. Implement `_read_supabase()` and `_write_supabase()` using S3-compatible Supabase Storage API
3. Support `STORAGE_TYPE=SUPABASE` env var
4. Add `SUPABASE_URL` and `SUPABASE_KEY` to `.env.example`
5. Add unit tests with mocked Supabase client

**Acceptance Criteria**
- [ ] `STORAGE_TYPE=SUPABASE` works end-to-end for read/write
- [ ] Fallback to `FILE` if supabase package not installed
- [ ] Unit tests cover Supabase backend (mocked)
- [ ] `.env.example` includes `SUPABASE_URL` and `SUPABASE_KEY`

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | geryon |
| Rationale | Multi-file implementation with new backend + tests |
| Priority | P2 — Asset storage for real audio pipeline |
| Branch | `geryon/add-supabase-storage` |
| Dependencies | HITL: Supabase instance credentials from Andrew |
```

---

#### Issue 11: [geryon] Add FastAPI endpoint tests for main_service.py

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: geryon
Source links: hive/main_service.py, tests/ (no main_service tests), pyproject.toml (pytest-asyncio)
Edit policy: Agent-editable

**Problem**
`main_service.py` contains 8+ API endpoints (`/health`, `/status`, `/trigger`, `/spawn`, `/webhook`,
`/ws/stream`, static mounts) with zero test coverage. The `/webhook` Stripe endpoint handles payment
verification — untested security-critical code.

**Proposed Solution**
Add `tests/test_main_service.py` using `fastapi.testclient.TestClient`:
- Test `/health` endpoint returns 200 with correct schema
- Test `/status` returns hive state
- Test `/trigger` validates required fields
- Test `/webhook` rejects requests without valid Stripe signature
- Test WebSocket `/ws/stream` connects and receives data
- Mock `QueenOrchestrator` to isolate FastAPI layer

**Acceptance Criteria**
- [ ] `tests/test_main_service.py` exists with ≥ 8 test cases
- [ ] All HTTP status codes are tested (200, 422, 503)
- [ ] Stripe webhook signature rejection is tested
- [ ] Tests run without real Gemini/Stripe credentials (all mocked)
- [ ] Coverage for `main_service.py` reaches ≥ 70%

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | geryon |
| Rationale | Multi-endpoint testing with async mocking complexity |
| Priority | P2 — Payment and API security coverage |
| Branch | `geryon/add-main-service-tests` |
| Dependencies | None |
```

---

#### Issue 12: [geryon] Add QueenOrchestrator unit tests

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: geryon
Source links: hive/queen/orchestrator.py (635 LOC), tests/ (no orchestrator tests)
Edit policy: Agent-editable

**Problem**
`orchestrator.py` (635 lines) is the core coordinator — zero test coverage. It manages bee
lifecycle, event dispatch, heartbeat, constitutional gateway integration, and failure tracking.
Bugs here silently stop the entire hive.

**Proposed Solution**
Add `tests/test_orchestrator.py`:
- Test bee registration and lookup
- Test `spawn_bee()` success and failure paths
- Test `trigger_event()` dispatching
- Test bee failure tracking and `MAX_BEE_FAILURES` circuit breaker
- Test `_load_config()` with missing/invalid config
- Mock all external dependencies (filesystem, Gemini, ConstitutionalGateway)

**Acceptance Criteria**
- [ ] `tests/test_orchestrator.py` exists with ≥ 10 test cases
- [ ] Bee failure circuit breaker behavior is tested
- [ ] Event dispatch routing is tested
- [ ] No real API calls made during tests
- [ ] Coverage for `orchestrator.py` reaches ≥ 60%

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | geryon |
| Rationale | Complex class with many dependencies, requires careful mocking |
| Priority | P2 — Core hive reliability |
| Branch | `geryon/add-orchestrator-tests` |
| Dependencies | None |
```

---

#### Issue 13: [copilot] Add CHANGELOG.md

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: copilot
Source links: pyproject.toml (v1.1.0), docs/roadmap_q1_2026.md, docs/session_manifest_jan_2026.md
Edit policy: Agent-editable; version entries require Andrew approval

**Problem**
No `CHANGELOG.md` exists. v1.1.0 is the current version with no documented history.
With multiple external integrations in flight (Stripe, Live365, Supabase), a changelog
is critical for operators and investors to track what changed between deployments.

**Proposed Solution**
Create `CHANGELOG.md` following [Keep a Changelog](https://keepachangelog.com) format:
- `[1.1.0]` — Backfill from session manifests and roadmap docs
- `[1.0.0]` — Initial hive deployment
- `[Unreleased]` — Changes on current branch

**Acceptance Criteria**
- [ ] `CHANGELOG.md` exists at repo root
- [ ] Follows Keep a Changelog format
- [ ] v1.1.0 entry documents DJ memory system, constitutional gateway, Gemini 2.0 upgrade
- [ ] Linked from README.md

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | copilot |
| Rationale | Documentation aggregation from existing session manifests |
| Priority | P2 — Release transparency |
| Branch | `copilot/add-changelog` |
| Dependencies | None |
```

---

### PHASE 3 ISSUES (Optimization — P3)

---

#### Issue 14: [geryon] Add retry/backoff logic to BaseBee

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: geryon
Source links: hive/bees/base_bee.py, hive/queen/orchestrator.py (MAX_BEE_FAILURES = 3)
Edit policy: Agent-editable

**Problem**
`BaseBee.run()` has no retry logic. Transient API failures (Gemini rate limits, network blips)
immediately count as bee failures against the orchestrator's `MAX_BEE_FAILURES` circuit breaker.
After 3 consecutive failures, the bee is blacklisted. This causes unnecessary hive degradation
during normal cloud service fluctuations.

**Proposed Solution**
Add `tenacity` (or simple exponential backoff) to `BaseBee.run()`:
- 3 retries with exponential backoff (1s, 2s, 4s)
- Retry on `requests.RequestException`, `ConnectionError`, `TimeoutError`
- Do NOT retry on `ValidationError` or `ValueError` (logic errors, not transient)
- Log each retry attempt at WARNING level

**Acceptance Criteria**
- [ ] `BaseBee.run()` retries transient failures up to 3 times
- [ ] Backoff intervals are exponential (not fixed)
- [ ] Logic errors (ValueError, ValidationError) are NOT retried
- [ ] Retry behavior is unit tested
- [ ] `tenacity` or backoff utility added to deps if used

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | geryon |
| Rationale | Core base class modification with test updates |
| Priority | P3 — Resilience improvement |
| Branch | `geryon/add-bee-retry-logic` |
| Dependencies | None |
```

---

#### Issue 15: [geryon] Add JSON structured logging for Cloud Run

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: geryon
Source links: hive/utils/logging.py, Dockerfile (Cloud Run target), README.md
Edit policy: Agent-editable

**Problem**
Current logging uses plain-text `[timestamp][BEE_TYPE] message` format. Cloud Run's log explorer
requires JSON-structured logs for filtering, correlation, and Cloud Monitoring integration.
Production debugging is impaired when logs cannot be queried by bee type, severity, or trace ID.

**Proposed Solution**
Update `hive/utils/logging.py` to emit JSON logs when `LOG_FORMAT=JSON` env var is set:
```json
{"timestamp": "...", "severity": "INFO", "bee": "trend_scout", "message": "..."}
```
- Keep plain-text format as default for local development
- JSON format for `LOG_FORMAT=JSON` (set in Dockerfile ENV)
- Include `bee_id`, `bee_type`, `trace_id` fields

**Acceptance Criteria**
- [ ] `LOG_FORMAT=JSON` produces valid JSON log lines
- [ ] Cloud Run Dockerfile sets `LOG_FORMAT=JSON`
- [ ] Plain text format unchanged for local dev (no `LOG_FORMAT` set)
- [ ] Log lines include `bee_type`, `severity`, `message`, `timestamp`
- [ ] Existing logging tests still pass

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | geryon |
| Rationale | Logging infrastructure change with test impact |
| Priority | P3 — Production observability |
| Branch | `geryon/structured-json-logging` |
| Dependencies | Issue #8 (Cloud Run deployment) |
```

---

#### Issue 16: [geryon] Implement Live365 audio stream control in DjBee

```
Status: ACTIVE
Tier: 1
Created: 2026-04-13
Owner: geryon
Source links: docs/GAP_ANALYSIS_REPORT.md §2.2, hive/bees/content/dj_bee.py, hive/utils/radio_bridge.py
Edit policy: Agent-editable; Live365 credentials require Andrew approval

**Problem**
`DjBee` simulates audio broadcast. `hive/utils/radio_bridge.py` contains placeholder Live365
integration. The station cannot actually play music without real Icecast/Live365 encoder control.
This is the core "actuator" gap — the hive can think but cannot broadcast.

**Proposed Solution**
Implement `hive/utils/radio_bridge.py`:
1. Connect to Live365 Icecast endpoint using `LIVE365_STATION_ID`, `LIVE365_USERNAME`, `LIVE365_PASSWORD`
2. Implement `push_audio(file_path)` — stream audio file to encoder
3. Implement `get_stream_status()` — check if stream is live
4. Implement `skip_track()` — send next-track signal
5. Update `DjBee.work()` to call radio_bridge instead of simulating
6. Add `LIVE365_*` vars to `.env.example`

**Acceptance Criteria**
- [ ] `radio_bridge.py` connects to a real Icecast endpoint (or Live365 API)
- [ ] `DjBee` calls `radio_bridge.push_audio()` when streaming is enabled
- [ ] Simulation mode remains available via `STREAM_MODE=SIMULATE` env var
- [ ] Integration test (marked `@pytest.mark.integration`) tests with real credentials
- [ ] Graceful fallback to simulation if Live365 unreachable

**Agent Surface Routing**
| Field | Value |
|-------|-------|
| Surface | geryon |
| Rationale | Complex audio streaming integration, requires Live365 API research |
| Priority | P3 (P1 after PikoClaw demo requirements confirmed by Andrew) |
| Branch | `geryon/live365-stream-control` |
| Dependencies | HITL: Live365 credentials and station ID from Andrew |
```

---

## Phase 5: Roadmap Tracker

### Backlink Broadcast — Development Roadmap 2026

| Phase | Issues | Surfaces | Exit Criteria |
|-------|--------|----------|---------------|
| **Phase 1: Foundation** | #1 LICENSE, #2 SECURITY.md, #3 CI Gates, #4 Dependabot, #5 Secrets Baseline | copilot, geryon | All P1 issues closed; CI gates enforced; repo legally compliant |
| **Phase 2: Hardening** | #6 CODEOWNERS, #7 CodeQL, #8 Cloud Run Deploy, #9 Stripe Dep, #10 Supabase, #11 API Tests, #12 Orchestrator Tests, #13 CHANGELOG | copilot, geryon | 70%+ coverage on critical paths; automated deployments working; payment infrastructure live |
| **Phase 3: Optimization** | #14 Retry Logic, #15 JSON Logging, #16 Live365 Stream | geryon | Real audio broadcasting; Cloud Run logs queryable; hive self-heals transient failures |

### Surface Distribution

| Surface | Issues | Count |
|---------|--------|-------|
| copilot | #1, #2, #4, #5, #6, #7, #9, #13 | 8 |
| geryon | #3, #8, #10, #11, #12, #14, #15, #16 | 8 |
| human (Andrew) | HITL items (Live365, Supabase, Stripe credentials, branch protection) | — |

### Dependency Graph

```
#1 LICENSE ──────────────────────────────► #6 CODEOWNERS
#2 SECURITY.md ──────────────────────────► (standalone)
#3 CI Gates ─────────────────────────────► #8 Cloud Run Deploy
#4 Dependabot ───────────────────────────► (standalone)
#5 Secrets Baseline ─────────────────────► (standalone)
#9 Stripe Dep ──────────────────────────► #11 API Tests (webhook)
#10 Supabase ────────────────────────────► (HITL gate)
#8 Cloud Run Deploy ─────────────────────► #15 JSON Logging
#16 Live365 ─────────────────────────────► (HITL gate: Andrew)
```

### Governing Principles

1. **Stigmergy First**: All bee changes must communicate via honeycomb, never direct.
2. **Constitutional Compliance**: Every new bee must integrate `ConstitutionalGateway`.
3. **4th Wall Integrity**: No implementation details leak into public DJ outputs.
4. **Security Gates Before Features**: Phase 1 must complete before Phase 2 merges.
5. **PikoClaw Demo Priority**: Features needed for Panathenea (May 27-29, 2026) are P1 regardless of phase.

---

## Phase 6: Cross-System Documentation

### Repo Artifacts Created This Session

| File | Action | Purpose |
|------|--------|---------|
| `LICENSE` | Created | MIT license file (was missing, declared in pyproject.toml) |
| `SECURITY.md` | Created | Vulnerability disclosure policy |
| `.github/pull_request_template.md` | Created | Consistent PR hygiene |
| `.github/dependabot.yml` | Created | Automated dependency updates |
| `.secrets.baseline` | ❌ Not created (absent on tip) | detect-secrets baseline still missing; Issue #5 remains open |
| `docs/agent-hydration.md` | Created | This hydration report |

### HITL Required (Andrew)

These items cannot proceed without human action:

| # | Item | Why HITL | Impact |
|---|------|----------|--------|
| 1 | **Stripe credentials** | Financial/API key setup | CommerceBee production mode |
| 2 | **Live365 station ID + credentials** | External account access | Real audio broadcasting |
| 3 | **Supabase instance URL + key** | External account setup | Media asset storage |
| 4 | **Branch protection rules** | GitHub settings UI | Enforce CI gates on merges |
| 5 | **PikoClaw demo feature list** | Product direction | P1 priority assignment |
| 6 | **WIF + GCP deploy SA for Cloud Run** (`WIF_PROVIDER`, `WIF_SERVICE_ACCOUNT`, project/region/service vars) | IAM/security — no JSON keys in repo | `deploy-cloud-run.yml` can leave dry-run / fail-closed until set; merge ≠ deploy |

### Recommended Next Action

**Start with Issue #3** (`[geryon] Fix CI: make Bandit and mypy blocking`) on the `geryon` surface.
This is the single most impactful foundation change — it converts the CI from decorative to
enforcing, which makes all subsequent quality improvements meaningful.

**Parallel track**: Andrew completes the HITL items (Stripe, Live365, Supabase credentials) to
unblock the Phase 2 payment + audio integration work.

---

*Generated by GitHub Copilot agent | fuzzywigg/Backlink | 2026-04-13*
