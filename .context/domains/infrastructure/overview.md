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

- **GitKraken / GitHub Actions**: (Implicit) CI/CD pipeline deploys on push to `main`.
- **Manual**: `gcloud run deploy` (See `docs/DEPLOYMENT_HANDOFF.md`).
