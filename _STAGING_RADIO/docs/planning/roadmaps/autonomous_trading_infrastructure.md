# Autonomous Trading Infrastructure Roadmap

## Phase 1: Stabilization (Current)

- [x] **Code Hardening**: Fixed UTF-8 logging bugs and set up dynamic risk sizing.
- [x] **Local Execution**: Bot is running stable on Primary Laptop.
- [ ] **Fueling**: Wallet `0x49F4...E1960` needs USDC on Polygon to start trading.
- [ ] **Observation**: Let runs for 24-48 hours to verify "Ghost Trade" handling and SFTP uplinks.

## Phase 2: The "Home Server" (Immediate Scale)

**Goal**: Move the bot off your laptop so you can close the lid without killing profits.

- [ ] **Provisioning**: specific setup of the "Second Computer" with Python and Git.
- [ ] **Migration**: Clone repo to the second computer and transfer `.env` (securely).
- [ ] **Remote Command**: Setup SSH or Remote Desktop to monitor the bot from your laptop.
- [ ] **Redundancy**: Use the laptop as a "Dev Environment" and the second computer as "Production".

## Phase 3: Cloud Integration (Future)

**Goal**: Professionalize the `g0p.us` dashboard using your purchased assets.

- [ ] **Cloudflare**:
  - Use for **DNS Management** of `g0p.us` (faster/safer than GoDaddy).
  - Enable **Cloudflare Access** (Zero Trust) to protect the dashboard info from public view if desired.
- [ ] **Google Cloud**:
  - If the "Home Server" fails deployment, we can use a **GCP Compute Instance** (e2-micro) for the bot.
  - Use **Google Storage** for archiving trade logs permanently.

## Action Plan

1. **Fund the Bot**: Send USDC to `0x49F408664951b142b8cf955b2191f75737cE1960` (Polygon Network).
2. **Transfer DNS**: Send me the Cloudflare details so we can route `app.g0p.us` through their fast CDN.
3. **Prep Server**: Turn on the second computer and install Python + Git.
