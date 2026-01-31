# Quick Start: Connecting External Services

This is a step-by-step checklist for connecting your GoDaddy, Cloudflare, and Firebase accounts to the Backlink Broadcast system.

## Prerequisites

- [ ] Access to your GoDaddy account (admin access)
- [ ] Access to your Cloudflare account (or ability to create one)
- [ ] Access to Firebase project `smtp-ai-5be89`
- [ ] GitHub repository admin access (to add secrets)

---

## Step 1: GoDaddy Hosting Setup (5 minutes)

### 1.1 Enable SSH Access

1. Log into your GoDaddy account
2. Go to **Web Hosting** → Select your hosting plan
3. Navigate to **cPanel** (or your control panel)
4. Find **SSH Access** section
5. Click **Manage SSH Keys**
6. Generate a new key pair or use an existing one
7. Download the **private key** file (keep it secure!)

### 1.2 Get Connection Details

You'll need:
- **SSH Host:** Your server IP or hostname (found in hosting details)
- **SSH User:** Your cPanel username
- **SSH Private Key:** The content of the private key file you downloaded

### 1.3 Add to GitHub Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret** for each:
   - Name: `SSH_HOST`, Value: `your-server-ip-or-hostname`
   - Name: `SSH_USER`, Value: `your-cpanel-username`
   - Name: `SSH_PRIVATE_KEY`, Value: `paste entire private key content`

### 1.4 Test Deployment

1. Go to **Actions** tab in GitHub
2. Find **Deploy to GoDaddy** workflow
3. Click **Run workflow** → **Run workflow**
4. Wait for completion (should turn green ✓)
5. Visit your GoDaddy domain to verify

---

## Step 2: Cloudflare Setup (10 minutes)

### 2.1 Add Domain to Cloudflare

1. Sign up for Cloudflare (free plan is fine)
2. Click **Add a site**
3. Enter your domain name
4. Select the **Free** plan
5. Cloudflare will scan your DNS records

### 2.2 Update Nameservers at GoDaddy

1. Cloudflare will show you 2 nameservers (e.g., `nam.ns.cloudflare.com`)
2. Copy these nameserver addresses
3. Go back to GoDaddy → **Domain Settings** → **Manage DNS**
4. Click **Change** next to Nameservers
5. Select **Custom** and paste the Cloudflare nameservers
6. Save changes (propagation takes 10-60 minutes)

### 2.3 Get Cloudflare API Token

1. In Cloudflare dashboard, click your profile → **API Tokens**
2. Click **Create Token**
3. Use **Edit zone DNS** template
4. Configure permissions:
   - Zone → DNS → Edit
   - Include → Specific zone → Your domain
5. Click **Continue to summary** → **Create Token**
6. **Copy the token** (you won't see it again!)

### 2.4 Get Zone ID

1. In Cloudflare dashboard, select your domain
2. Scroll down on Overview page
3. Find **Zone ID** in the right sidebar
4. Copy the Zone ID

### 2.5 Add to Repository

**For Local Development:**
Edit `.env` file (create if it doesn't exist):
```bash
CLOUDFLARE_API_TOKEN=your_token_here
CLOUDFLARE_ZONE_ID=your_zone_id_here
```

**For GitHub Actions:**
Add as secrets:
- Name: `CLOUDFLARE_API_TOKEN`, Value: your token
- Name: `CLOUDFLARE_ZONE_ID`, Value: your zone ID

### 2.6 Configure DNS Records

In Cloudflare DNS settings, add:

```
Type    Name    Content                          Proxy Status
A       @       [Your GoDaddy Server IP]         Proxied
CNAME   www     yourdomain.com                   Proxied
CNAME   api     backlink-hive-[...].run.app      Proxied
```

---

## Step 3: Firebase Configuration (5 minutes)

### 3.1 Verify Access

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Find project **smtp-ai-5be89**
3. Verify you have **Owner** or **Editor** role

### 3.2 Install Firebase CLI

```bash
npm install -g firebase-tools
```

### 3.3 Authenticate

```bash
firebase login
```

This will open a browser for you to authenticate with Google.

### 3.4 Test Deployment

```bash
# From repository root
firebase deploy --only hosting --project smtp-ai-5be89
```

### 3.5 Connect Custom Domain (Optional)

1. In Firebase Console → **Hosting**
2. Click **Add custom domain**
3. Enter your domain name
4. Firebase will provide DNS records
5. Add these records in Cloudflare DNS
6. Wait for verification (can take up to 24 hours)

---

## Step 4: Environment Variables Setup

### 4.1 Create Local `.env` File

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

### 4.2 Fill in Values

Edit `.env` with your actual values:

```bash
# Google Cloud / Firebase
GCP_PROJECT_ID=smtp-ai-5be89
STORAGE_TYPE=FIRESTORE
GOOGLE_API_KEY=your_gemini_api_key_here
HIVE_SECRET_KEY=generate_a_uuid_here

# Cloudflare
CLOUDFLARE_API_TOKEN=your_token_from_step_2
CLOUDFLARE_ZONE_ID=your_zone_id_from_step_2

# Other services (optional)
TWITTER_API_KEY=
TWITTER_API_SECRET=
```

### 4.3 Generate Secrets

For `HIVE_SECRET_KEY`, run:

```bash
python -c "import uuid; print(uuid.uuid4())"
```

Copy the output and paste into `.env`

---

## Step 5: Verification

### 5.1 Test GoDaddy Deployment

Visit: `https://yourdomain.com`

Should show your documentation site.

### 5.2 Test Firebase Hosting

Visit: `https://smtp-ai-5be89.web.app`

Should show your application.

### 5.3 Test Cloud Run API

Visit: `https://backlink-hive-[...].run.app/health`

Should return: `{"status": "ok"}`

### 5.4 Test DNS Resolution

```bash
# Check if Cloudflare is active
nslookup yourdomain.com

# Should show Cloudflare IPs if proxied
dig yourdomain.com
```

---

## Step 6: Continuous Deployment

Once everything is configured, deployments happen automatically:

### GoDaddy Documentation
- **Trigger:** Push to `main` branch with changes to `docs/**`
- **What deploys:** MkDocs static site
- **Where:** `~/public_html` on your GoDaddy server

### Firebase Hosting
- **Trigger:** Run `firebase deploy --only hosting`
- **What deploys:** Static frontend files from `public/`
- **Where:** `smtp-ai-5be89.web.app`

### Cloud Run (Hive Backend)
- **Trigger:** Use `gcloud` CLI or Cloud Build
- **What deploys:** Docker container with Python backend
- **Where:** `backlink-hive-[...].run.app`

---

## Troubleshooting

### GoDaddy Deployment Fails

- Check GitHub Actions logs for SSH errors
- Verify SSH key is correct (no extra spaces or line breaks)
- Test SSH manually: `ssh username@hostname`
- Ensure `~/public_html` directory exists and is writable

### Cloudflare Not Working

- Wait 10-60 minutes for nameserver propagation
- Check nameservers: `dig NS yourdomain.com`
- Verify API token has correct permissions
- Check Zone ID matches your domain

### Firebase Deploy Fails

- Run `firebase login` again
- Check you're in correct project: `firebase use smtp-ai-5be89`
- Verify `firebase.json` is valid JSON
- Check Firebase Console for error messages

---

## Summary Checklist

- [ ] GoDaddy SSH credentials added to GitHub Secrets
- [ ] GoDaddy deployment workflow tested successfully
- [ ] Cloudflare nameservers updated at GoDaddy
- [ ] Cloudflare API token generated and saved
- [ ] Cloudflare DNS records configured
- [ ] Firebase CLI installed and authenticated
- [ ] Firebase deployment tested
- [ ] `.env` file created with all credentials
- [ ] Custom domain connected (optional)
- [ ] All services verified and working

---

## Need Help?

- **Full documentation:** See `docs/EXTERNAL_SERVICE_INTEGRATION.md`
- **Deployment guide:** See `docs/DEPLOYMENT_HANDOFF.md`
- **Configuration:** See `.env.example` for all variables
- **Workflows:** Check `.github/workflows/` for CI/CD examples

---

**Important:** Never commit your `.env` file or real credentials to the repository. They are already in `.gitignore`.
