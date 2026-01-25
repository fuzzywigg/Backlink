# UHI PRODUCT MANIFEST

This directory tracks the active "High Income" services deployed by the Hive.

## ACTIVE PRODUCTS

1. **[The Watchtower](watchtower_service_def.json)**
    * **Status:** MVP Ready
    * **Type:** Security Tool
    * **Price:** $50 Lifetime
    * **Pipeline:** Ready for packaging.

2. **[The Honeycomb](../honeypot_core/honeycomb_service_def.json)**
    * **Status:** MVP Ready
    * **Type:** Decoy Defense
    * **Price:** $50 Lifetime
    * **Pipeline:** Packaged.

3. **[The Auditor](../auditor_core/README.md)**
    * **Status:** Prototype Ready
    * **Type:** Compliance Tool
    * **Price:** Free / Pro
    * **Pipeline:** Script Available.

## PLANNED PRODUCTS

1. **The Curator** (Data Service)
2. **The Artisan** (Content Service)

## DEPLOYMENT PROTOCOL

To launch a new product:

1. Create `[name]_service_def.json` following the schema.
2. Build the code in `hive/products/[name]/`.
3. Set `operator_wallet` to the Iron Dome Vault (`0x9d27...`).
