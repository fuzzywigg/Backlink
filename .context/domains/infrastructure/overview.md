# Domain: Infrastructure

## Cloud Run & Containerization

The project is deployed as a single container on **Google Cloud Run**.

### Docker

- Base Image: `python:3.11-slim`
- Entrypoint: `uvicorn hive.main_service:app`
- Port: 8080 (Mapped via `$PORT`)

### Firebase & Firestore

- **Database**: Firestore (Native Mode).
- **Emulators**: Used for local development (`firebase emulators:start`).
- **Config**: `firebase.json` and `.firebaserc`.

### Deployment

- **GitHub Actions**: `.github/workflows/deploy-cloud-run.yml` — `workflow_dispatch` only
  (no push-to-`main` auto-deploy). Defaults: `dry_run=true`, `promote=false` (0% traffic).
  Image/traffic tag form: `tip-<12-char-sha>`. Confirm live tip via `/health` provenance.
- **Manual emergency**: `gcloud run deploy` sketch in `docs/DEPLOYMENT_HANDOFF.md`.
