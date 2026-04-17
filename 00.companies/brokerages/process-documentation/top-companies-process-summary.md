# Texas Brokerage Intelligence Research Process

This document describes the methodology, tools, and automation scripts used by Gemini to research and document the top 100 Texas brokerages as of March 2026.

## 1. Process Overview

### Phase 1: Foundation & Extraction
- **Source Selection:** Utilized the master TREC data dump in `source/trec/` (e.g., `Broker_and_Sales_Agent_License_Holder_Information_YYYYMMDD.csv`).
- **Initial Filtering:** Extracted the top 100 entities based on "Total Active Sales Agents" for March 2026 into `output/summaries/`.
- **Goal:** Establish a clean baseline of legal names, license numbers, and agent counts.

### Phase 2: Technical Discovery
- **Transition from UI to API:** Initial research used Playwright browser automation to scrape `trec.texas.gov`.
- **API Identification:** Discovered TREC's internal JSON API endpoint (`https://www.trec.texas.gov/acaif/api/licenseDetail/{LicenseNumber}`).
- **Optimization:** Shifted to direct API requests, which increased extraction speed by 10x and improved fidelity for complex arrays like "DBAs" and "Team Names."

### Phase 3: Intelligence Enrichment
- **Mandatory Manual & AI Research:** EVERY company in the set must undergo manual verification via Google Web Search to resolve:
    - **Headquarters:** Locating the corporate hub.
    - **Presence:** Determining if the firm is local, national, or global.
    - **Type:** Classifying as Independent, Franchise, or Tech Platform.
    - **Main City:** Identifying the primary Texas market hub.
    - **Website URL:** Validating official domains.
- **Automation Support:** Use `batch_metadata_update.py` for initial triage of large franchises, but follow with manual verification for all remaining entries.
- **Persistence Strategy:** Used Python scripts to incrementally update the CSV file, ensuring progress was saved even if research turns were interrupted.

### Phase 4: Structural Finalization
- **Information Hierarchy:** Reorganized columns to place "high-signal" intelligence (HQ, Type, URL) immediately after the Company Name.
- **Metro Area Mapping:** Classified all "Main City" values into broader metropolitan regions (e.g., DFW, Houston, Austin, San Antonio, El Paso, McAllen / RGV) to facilitate regional sales reporting.
- **Cleanup:** Sanitized messy team name strings and standardized city names.

### Phase 5: Production & GCI Analysis
- **Roster Extraction:** Identify all active agents associated with a brokerage license from the master TREC data.
- **MLS Integration:** Query the `mls.property` database to retrieve closed transaction sides for the extracted roster over the last 12 months.
- **Production Metrics:** Calculate Gross Commission Income (GCI) for both sales and leases.
- **Revenue Share Modeling:** Estimate potential earnings from Jointly's ancillary services (Lease Applications and Concierge) based on the brokerage's production volume.
- **Producer Identification:** Rank the top 5 sales and lease producers to identify key targets for platform adoption.

### Phase 6: Quality Assurance & Validation
- **Logic Cross-Reference:** Always cross-reference `calculate_mrr.py` logic against the official `pricing-structure.md`.
- **API Health Check:** Verify the TREC API response structure before batch processing; ensure `User-Agent` headers are active to avoid 403 Forbidden errors.
- **Data Completeness:** Audit the final CSV for "NULL" or empty strings in high-value columns like DBAs, Website, and MRR.

---

## 2. Tools Used

- **Python (Pandas/CSV):** For data processing, sorting, and structural manipulation.
- **TREC Background API:** The definitive source for licensing and relationship data. Requires specific headers for access.
- **MLS Database:** Production source for transaction history and volume analysis.
- **Playwright:** Initially for web browsing; later for verifying dynamic content on brokerage sites.
- **Google Search:** For resolving corporate structure and headquarters for national entities.
- **Gemini CLI:** The orchestration layer managing task delegation and data persistence.

---

## 3. Automation Scripts

The following scripts are maintained in `./scripts` and should be used for every refresh:

| Script | Purpose |
| --- | --- |
| `enrich_brokerages.py` | Connects to TREC API. **Mandatory:** Uses headers to avoid 403s and parses list-based JSON for DBAs/Teams. |
| `reorder_columns.py` | Enforces the strict column order requested by the growth team. |
| `add_metro_area.py` | Maps Main City to broader Metro Areas (DFW, Houston, etc.). |
| `batch_metadata_update.py` | Bulk updates Type, HQ, and Presence fields. |
| `calculate_mrr.py` | Calculates MRR. **Constraint:** Must match `pricing-structure.md` tiers exactly. |
| `brokerage_deep_dive.py` | Extracts agent rosters and queries production data. |
| `enrich_top_100_production.py` | Batch processes lists to append production and revenue opportunity data. |

---

## 4. Key Reference Documents

- **`pricing-structure.md`**: Defines the base fee and tiered seat rates for Jointly Business.

*Detailed script contents are available in the `./scripts` subfolder.*
