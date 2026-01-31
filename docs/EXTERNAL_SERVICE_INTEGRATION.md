# External Service Integration Guide

**Document Purpose:** Clarify AI agent capabilities for external service integration and provide setup instructions for GoDaddy, Cloudflare, and Firebase.

---

## Understanding AI Agent Capabilities

### What AI Agents CAN Do

✅ **Configure Local Files**
- Create and modify configuration files (`.env`, `config.json`, YAML files)
- Set up deployment scripts and CI/CD workflows
- Generate integration code and API client implementations
- Update documentation and setup instructions

✅ **Prepare Infrastructure Code**
- Write Terraform/Infrastructure-as-Code configurations
- Create Docker configurations for deployment
- Set up GitHub Actions workflows
- Configure DNS settings (as code/documentation)

✅ **Work With Repository Content**
- Analyze existing integrations
- Suggest best practices for service connections
- Create wrapper libraries for external APIs
- Document authentication flows

### What AI Agents CANNOT Do

❌ **Direct Account Access**
- Cannot log into your GoDaddy account
- Cannot access your Cloudflare dashboard
- Cannot make API calls to external services without credentials
- Cannot view or modify your actual DNS records directly

❌ **Interactive Authentication**
- Cannot complete OAuth flows requiring browser interaction
- Cannot respond to 2FA prompts
- Cannot generate API tokens from service dashboards

---

## Current Integration Status

Based on repository analysis:

| Service | Status | Configuration Found | Notes |
|---------|--------|---------------------|-------|
| **Firebase/Google Cloud** | ✅ Configured | `.firebaserc`, `firebase.json` | Project: `smtp-ai-5be89` |
| **GoDaddy** | ⚙️ Partial | `.github/workflows/deploy_godaddy.yml` | Deployment workflow exists, needs secrets |
| **Cloudflare** | 📋 Planned | `config/target_apis.json` | Listed as "pending_auth" |
| **Google Cloud Run** | ✅ Active | `DEPLOYMENT_HANDOFF.md` | Production deployment configured |

---

## Setting Up External Services

### 1. GoDaddy Integration

Your GoDaddy deployment is already configured via GitHub Actions!

**What You Need:**

1. **SSH Access to Your GoDaddy Hosting**
   - Log into your GoDaddy account
   - Go to your hosting control panel
   - Enable SSH access (cPanel → SSH Access)
   - Generate or obtain your SSH private key

2. **Configure GitHub Secrets**
   
   Go to your GitHub repository → Settings → Secrets → Actions, and add:
   
   ```
   SSH_HOST          : Your GoDaddy server hostname (e.g., ip-address or domain)
   SSH_USER          : Your cPanel username or SSH username
   SSH_PRIVATE_KEY   : Your SSH private key (the entire key content)
   ```

3. **Deploy**
   
   The workflow (`.github/workflows/deploy_godaddy.yml`) will automatically:
   - Build your MkDocs site
   - Deploy to `~/public_html` on your GoDaddy server
   - Trigger on pushes to `main` branch or manual dispatch

**Current Workflow Capabilities:**
- ✅ Builds documentation site with MkDocs
- ✅ Deploys via SCP to GoDaddy hosting
- ✅ Includes wisdom.json API endpoint
- ✅ Auto-deploys on documentation changes

### 2. Cloudflare Integration

Cloudflare can enhance your deployment with:
- DNS management
- CDN/caching
- DDoS protection
- Workers for serverless functions

**Setup Steps:**

1. **Get Your Cloudflare API Token**
   
   - Log into Cloudflare dashboard
   - Go to My Profile → API Tokens
   - Create Token → "Edit zone DNS" template
   - Copy the generated token

2. **Add to Environment Variables**
   
   Create or update `.env`:
   ```bash
   CLOUDFLARE_API_TOKEN=your_token_here
   CLOUDFLARE_ZONE_ID=your_zone_id_here
   ```

3. **Add to GitHub Secrets** (for CI/CD)
   
   ```
   CLOUDFLARE_API_TOKEN : Your API token
   CLOUDFLARE_ZONE_ID   : Your zone ID (found in Cloudflare dashboard)
   ```

4. **Configure DNS Records**
   
   You can manage DNS via:
   - **Cloudflare Dashboard** (manual, recommended for initial setup)
   - **Terraform** (infrastructure as code)
   - **API calls** (automated updates)

**Recommended DNS Setup:**
```
Type    Name              Value                          Proxy
A       @                 [Your GoDaddy Server IP]       ✅ Proxied
CNAME   www               yourdomain.com                 ✅ Proxied
CNAME   api               backlink-hive-*.run.app        ✅ Proxied
```

### 3. Firebase/Google Cloud (Already Configured!)

Your Firebase project is already set up:
- **Project ID:** `smtp-ai-5be89`
- **Configuration:** `.firebaserc`, `firebase.json`
- **Deployment:** Use `firebase deploy --only hosting`

**Enhanced Setup:**

1. **Install Firebase CLI**
   ```bash
   npm install -g firebase-tools
   ```

2. **Authenticate**
   ```bash
   firebase login
   ```

3. **Deploy Hosting**
   ```bash
   firebase deploy --only hosting --project smtp-ai-5be89
   ```

4. **Deploy Firestore Rules**
   ```bash
   firebase deploy --only firestore --project smtp-ai-5be89
   ```

**Connect Custom Domain (via Firebase):**
1. Firebase Console → Hosting
2. "Add custom domain"
3. Follow DNS verification steps
4. Add provided DNS records to your GoDaddy or Cloudflare

---

## Automation Recommendations

### Option 1: Single Source of Truth (Recommended)

**Use Firebase Hosting as Primary + Cloudflare DNS**

```
User Request → Cloudflare DNS → Firebase Hosting → Your Content
```

Benefits:
- ✅ Automatic SSL
- ✅ Global CDN
- ✅ No server management
- ✅ Cloudflare security

Setup:
1. Point your domain DNS (in GoDaddy or Cloudflare) to Firebase
2. Use Cloudflare for DNS management only (not proxied)
3. Let Firebase handle hosting

### Option 2: Dual Deployment

**GoDaddy for Docs, Firebase for App**

```
docs.yourdomain.com   → GoDaddy (via GitHub Actions)
app.yourdomain.com    → Firebase Hosting
api.yourdomain.com    → Cloud Run
```

Setup:
1. Configure subdomains in Cloudflare:
   - `docs` → GoDaddy server IP
   - `app` → Firebase hosting
   - `api` → Cloud Run URL
2. Each service deploys independently

### Option 3: Full Cloud Run + Cloudflare

**Everything on Cloud Run with Cloudflare CDN**

```
User → Cloudflare (DNS/CDN) → Cloud Run (Container)
```

Benefits:
- ✅ Maximum control
- ✅ Single deployment target
- ✅ Cloudflare caching/security

---

## Required Actions from You

To enable full integration, you need to:

### 1. Provide Credentials (Securely)

**For GitHub Actions:**
- [ ] Add `SSH_HOST`, `SSH_USER`, `SSH_PRIVATE_KEY` to GitHub Secrets (for GoDaddy)
- [ ] Add `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ZONE_ID` (if using Cloudflare automation)

**For Local Development:**
- [ ] Create `.env` file with service credentials (use `.env.example` as template)
- [ ] Never commit real credentials to the repository

### 2. Service Configuration

**GoDaddy:**
- [ ] Verify SSH access is enabled
- [ ] Confirm deployment target directory (`~/public_html` is correct)
- [ ] Test SSH connection manually: `ssh username@hostname`

**Cloudflare:**
- [ ] Add your domain to Cloudflare (if not already)
- [ ] Update nameservers at GoDaddy to point to Cloudflare
- [ ] Configure desired DNS records

**Firebase:**
- [ ] Verify you have owner/editor access to project `smtp-ai-5be89`
- [ ] Run `firebase login` and confirm authentication
- [ ] Test deployment with `firebase deploy`

### 3. Testing & Verification

After setup:
1. Trigger GoDaddy deployment (push to main or workflow dispatch)
2. Check `https://yourdomain.com` for documentation
3. Verify Firebase deployment: `https://smtp-ai-5be89.web.app`
4. Test Cloud Run API: `https://backlink-hive-*.run.app/health`

---

## Environment Variables Summary

Complete list of environment variables for all services:

```bash
# Google Cloud / Firebase
GCP_PROJECT_ID=smtp-ai-5be89
STORAGE_TYPE=FIRESTORE
GOOGLE_API_KEY=your_gemini_api_key
HIVE_SECRET_KEY=generate_a_uuid

# Cloudflare (Optional)
CLOUDFLARE_API_TOKEN=your_token
CLOUDFLARE_ZONE_ID=your_zone_id

# Social Media (Optional)
TWITTER_API_KEY=your_key
TWITTER_API_SECRET=your_secret
TWITTER_ACCESS_TOKEN=your_token
TWITTER_ACCESS_TOKEN_SECRET=your_secret

# Other Services (Optional)
BROWSER_USE_API_KEY=your_key
API_NINJAS_KEY=your_key
```

---

## Next Steps

1. **Review this document** and decide on your preferred architecture (Option 1, 2, or 3)
2. **Gather credentials** from GoDaddy, Cloudflare, and Firebase
3. **Configure GitHub Secrets** for automated deployments
4. **Test each integration** independently before combining
5. **Update DNS records** to connect everything together

---

## Getting Help

If you need assistance with:
- **Credential generation:** Consult service documentation (links in README)
- **CI/CD setup:** Check `.github/workflows/` for working examples
- **DNS configuration:** See Cloudflare/GoDaddy documentation
- **Deployment issues:** Check Cloud Run logs via `gcloud` CLI or GCP Console

---

**Remember:** AI agents can prepare all the code and configuration, but you must provide the authentication credentials and trigger the actual service connections.
