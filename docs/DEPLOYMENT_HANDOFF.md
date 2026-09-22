# ANDON LABS - DEPLOYMENT INITIATION PROTOCOL

**TARGET AUDIENCE:** Andon Labs Development Team / Payment Portal LLM Agent  
**PURPOSE:** Initialization of Hive Infrastructure (Cloud Run + Firestore)

---

To the initialization Agent:
Please execute the following setup sequence to prepare the Backlink Hive for deployment.

## 1. Google Cloud Platform Provisioning

**Context:** The Hive requires a stateless container runtime (Cloud Run) and a persistent NoSQL document store (Firestore) to maintain memory of the "Queen" and her "Bees" (Agents).

### Action Checklist

- [ ] **Create/Select Project:** Ensure a GCP Project exists (e.g., `andon-backlink-hive-prod`).
- [ ] **Enable APIs:**
  - `run.googleapis.com` (Cloud Run)
  - `firestore.googleapis.com` (Firestore)
  - `artifactregistry.googleapis.com` (Container Registry)
  - `cloudbuild.googleapis.com` (Cloud Build)
- [ ] **Initialize Firestore:**
  - **CRITICAL:** Select **Native Mode** (not Datastore mode).
  - **Region:** Recommended `us-central1` (or match Cloud Run region).
  - **Collection:** The app defaults to using a root collection named `hive_data`. No manual schema creation is needed; the Storage Adapter will create documents on first write.

## 2. Environment Configuration (The "Genesis Config")

The following environment variables must be injected into the Cloud Run service at deployment time.

| Variable | Required | Description | Example Value |
| :--- | :--- | :--- | :--- |
| `GCP_PROJECT_ID` | **YES** | The Project ID where Firestore lives. | `andon-backlink-hive` |
| `STORAGE_TYPE` | **YES** | Switches storage from local file to cloud. | `FIRESTORE` |
| `HIVE_SECRET_KEY` | **YES** | Used to HMAC sign state changes. | `(Generate a strong UUID)` |
| `OPENAI_API_KEY` | **YES** | Powering the LLM brains. | `sk-...` |
| `TWITTER_API_KEY` | No | If `SocialPosterBee` is active. | `...` |
| `TWITTER_API_SECRET` | No | If `SocialPosterBee` is active. | `...` |
| `BROWSER_USE_API_KEY`| No | If using Browser Use for deep scraping. | `...` |

## 3. Deployment Instruction (CLI)

Once prerequisites are met, deploy the Hive using the generated Dockerfile:

```bash
# 1. Build image with non-secret provenance (issue #89)
GIT_SHA=$(git rev-parse --short HEAD)
docker build \
  --build-arg GIT_SHA=${GIT_SHA} \
  --build-arg BUILD_TIMESTAMP=$(date -u +%Y%m%d_%H%M) \
  -t gcr.io/PROJECT_ID/backlink-hive .
docker push gcr.io/PROJECT_ID/backlink-hive

# Alternative: gcloud builds submit --tag gcr.io/PROJECT_ID/backlink-hive
# (pass GIT_SHA via Dockerfile ARG in your Cloud Build config, or set
# GIT_SHA / COMMIT_SHA / SOURCE_COMMIT on the Cloud Run service env)

# 2. Deploy to Cloud Run
gcloud run deploy backlink-hive \
  --image gcr.io/PROJECT_ID/backlink-hive \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \  # (Or --no-allow-unauthenticated for internal only)
  --set-env-vars STORAGE_TYPE=FIRESTORE,GCP_PROJECT_ID=PROJECT_ID,HIVE_SECRET_KEY=SECRET
```

> **Build provenance:** Bake `GIT_SHA` (and optionally `BUILD_ID` / `BUILD_TIMESTAMP`) into the
> image via Dockerfile `ARG`/`ENV` at build time. Do not put secrets in these fields. If unset,
> `/health` reports `git_sha: "unknown"`. The handler also accepts `SOURCE_COMMIT` or
> `COMMIT_SHA` (Cloud Build default) and optional `BUILD_ID`.

## 4. Verification

After deployment, access the service URL:

- `/health` -> JSON with `status`, `version`, `uptime_seconds`, `hive_status`, plus non-secret
  `git_sha` (and optional `build_id` / `build_time`). Compare `git_sha` to tip
  `git rev-parse --short HEAD` (or full SHA) to confirm the revision that is live —
  no `gcloud run services describe` required for this check.
- `/` -> Should load the Dashboard HTML.
