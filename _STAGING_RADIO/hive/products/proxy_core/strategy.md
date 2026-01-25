# THE PROXY: Sovereign Browser Agent (Stream 6)

**Philosophy:** "The User signs. The Agent surfs."

## THE PROBLEM

Web3 frontends (Uniswap, Aave, OpenSea) track IP addresses and user metadata. Interacting with them directly leaks privacy. Furthermore, many frontends restrict access based on Geo-IP.

## THE PRODUCT

A headless browser agent (using Puppeteer/Playwright) that navigates the frontend, constructs the transaction, and delivers the **Unsigned Transaction Object** to the user via the Iron Dome Protocol.

## MECHANISM

1. **Request:** User says "Swap 100 USDC for ETH on Uniswap."
2. **Navigation:** Agent launches a headless browser (via VPN/Proxy), goes to app.uniswap.org.
3. **Simulation:** Agent interacts with the UI to generate the calldata.
4. **Extraction:** Agent intercepts the wallet connection request or transaction payload.
5. **Delivery:** Agent creates a `proposal.json` (Iron Dome format).
6. **Execution:** User signs offline and broadcasts via a clean RPC.

## VALUE PROP

* **Privacy:** Site never sees the User's real IP.
* **Security:** User never connects their Ledger to a potentially compromised frontend (Phishing protection).
* **Automation:** Can schedule DCA (Dollar Cost Averaging) without giving the bot keys.

## ARCHITECTURE (MVP)

* **Tech:** Python + Selenium or Playwright.
* **Inputs:** `proxy_config.json` (Target URL, Action).
* **Outputs:** `proposal.json`.

## UHI STATUS

* **Phase:** Research & Prototype.
* **Stream:** #6 (Privacy / Operations).
