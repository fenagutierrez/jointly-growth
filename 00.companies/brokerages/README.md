# Texas Brokerage Intelligence & Prospecting System

This directory serves as the centralized intelligence hub for Jointly's growth team, focusing on Texas real estate brokerages. It contains structured profiles, raw licensing data, and automated processing workflows to identify high-signal prospecting opportunities.

## 📁 Directory Structure

- **`profiles-tier-1/`**: Research profiles for high-velocity and large-scale brokerages (Tier 1 targets). Organized alphabetically (A-Z).
- **`profiles-tier-3/`**: Research profiles for smaller "Squeezed Boutiques" (Tier 3 targets, typically 5-10 agents). Organized alphabetically (A-Z).
- **`source/`**:
    - **`trec/`**: Raw monthly license holder data dumps from the Texas Real Estate Commission (TREC).
- **`output/`**:
    - **`summaries/`**: Processed CSV files, including master lists of active brokers and the "Top 100" high-productivity targets.
- **`process-documentation/`**:
    - **`trec-data-processing/`**: Standard Operating Procedures (SOPs) for handling monthly data refreshes.
    - **`templates/`**: Markdown templates for consistent profile generation.
    - **`scripts/`**: Automation tools for data enrichment, MRR calculation, and production analysis.

---

## ⚙️ Core Processes

### 1. Monthly TREC Data Refresh
A monthly cycle to ingest raw TREC data, calculate active agent counts per license holder, and identify new brokerages entering our target ranges (5-10 agents for Tier 3).
- **SOP:** `process-documentation/trec-data-processing/TREC_data_process.md`
- **Output:** Updates the master summary in `output/summaries/`.

### 2. Brokerage Deep-Dive Research
A systematic process to move a brokerage from a "raw license entry" to a "high-signal prospect profile." This involves auditing their digital presence, tech stack, and transaction velocity.
- **SOP:** `process-documentation/brokerage-deep-dive-research.md`
- **Automation:** Uses the `brokerage_deep_dive.py` script (located in `04.dev/scripts/`) to pull 12-month trailing production data directly from the MLS for every agent on the roster.

### 3. Production & Revenue Analysis
We perform a 100% full-roster analysis to calculate:
- **GCI:** Gross Commission Income based on actual sales (3%) and leases (50% of one month's rent).
- **Business Mix:** The ratio of Sales vs. Leases by unit volume.
- **Potential Revenue Share:** Estimated revenue Jointly could generate from Lease Applications ($28/listing) and Concierge services ($42/opt-in).

---

## 🛠️ Automation Tools

| Script | Purpose |
| --- | --- |
| `enrich_brokerages.py` | Fetches live DBA and Team name lists from the TREC API. |
| `calculate_mrr.py` | Calculates Monthly Recurring Revenue based on our tiered seat pricing. |
| `reorder_columns.py` | Enforces the information hierarchy in growth CSVs. |
| `brokerage_deep_dive.py` | (In Dev Folder) Automates full-roster MLS production queries. |

---

## 📄 Key Reference Documents

- **[Jointly Business Pricing Structure](process-documentation/pricing-structure.md)**: Details the base fee and tiered seat rates.
- **[Profile Template](process-documentation/templates/template.md)**: The mandatory structure for all brokerage profiles.
