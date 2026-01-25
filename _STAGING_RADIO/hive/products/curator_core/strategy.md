# THE CURATOR: Sovereign Data Service (Stream 4)

**Philosophy:** "In the age of AI noise, clean data is the new gold."

## THE PRODUCT

An autonomous agent that ingests raw, messy data (CSVs, Logs, Web Scrapes) and outputs "Golden Records"—verified, structured, and enriched datasets ready for RAG (Retrieval-Augmented Generation) or machine learning.

## TARGET CUSTOMER

* **AI Developers:** Who need clean data for fine-tuning.
* **DeFi Analysts:** Who need structured blockchain event logs.
* **Media Companies:** Who need metadata enrichment (e.g., our own Backlink Radio).

## CORE MECHANISM

1. **Ingest:** Accepts standard formats (CSV, JSON, SQL dump).
2. **Sanitize:** Removes PII, duplicates, and nulls.
3. **Enrich:** Uses an LLM (Gemini/GPT) to add context, summary, or missing fields.
4. **Verify:** Checks against a "Golden Schema".
5. **Mint:** (Optional) Hashes the dataset and timestamps it on-chain as a "Data NFT" (Proof of Provenance).

## UHI PACKAGING

* **Price:** $0.01 per record processed (Micro-payment).
* **Interface:** CLI or API.
* **Infrastructure:** Python + Pandas + LLM API.

## IMMEDIATE USE CASE

We will use *The Curator* to clean our own **Music Library** (`andon-fm-metadata.csv`) and turn it into the `intel.json` format we need for the radio. This proves the product works ("Dogfooding").
