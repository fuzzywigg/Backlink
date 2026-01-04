# Deploy Radio Dashboard to Firebase Hosting
Write-Host "Deploying Radio Fuzzywigg to Firebase..."
firebase deploy --only hosting --project smtp-ai-5be89
# Note: User needs to ensure 'fuzzywigg-radio' (or correct project ID) is set or passed via --project
# If project not created, they might need to run `firebase projects:create` or similar.
# For now, we assume standard 'firebase deploy' works if .firebaserc is set, or they select interactively.
Write-Host "Deployment command sent. Check output."
