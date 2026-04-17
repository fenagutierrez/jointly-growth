# Texas Real Estate Team Intelligence Research Process

This document describes the methodology and automation steps used to enrich Texas real estate team data with contact intelligence and financial metrics.

## 1. Process Overview

### Phase 1: Structural Setup
- **Baseline:** Utilize existing team CSVs (e.g., `all_medium_teams_texas.csv`) sourced from RealTrends.
- **Schema Expansion:** Add the following high-signal columns:
    - `teamLeadName`: The primary licensed agent leading the group.
    - `teamLeadEmail`: Direct professional email for the lead.
    - `teamLeadPhone`: Direct or primary business line for the lead.
    - `mrr`: Estimated monthly recurring revenue for Jointly Business.
    - `metroArea`: Broad metropolitan region (e.g., DFW, Houston).
- **Information Hierarchy:** Reorder columns to place sales-ready data at the front.

### Phase 2: Technical & Automated Enrichment
- **Metro Area Mapping:** Map the `location` field (e.g., "Katy, TX") to one of the major Texas metros:
    - **Houston**, **DFW**, **Austin**, **San Antonio**, **El Paso**, **RGV**, or **Other TX**.
- **MRR Calculation:** Apply the tiered pricing model from `pricing-structure.md`:
    - Base: $249 (includes 5 seats).
    - Tier 2 (6-25 seats): +$25/seat.
    - Tier 3 (26-49 seats): +$15/seat.
- **Automation Script:** Use `enrich_teams_automation.py` to perform these batch calculations.

### Phase 3: Contact Intelligence Research
- **Lead Identification:** Cross-reference `teamName` and `url` (RealTrends) with the TREC database to find the primary licensee.
- **Web Verification:** Use Google Search and official team websites to resolve:
    - **Direct Email:** Priority on `@teamname.com` or `@brokerage.com` addresses.
    - **Direct Phone:** Verification of the team's primary business contact.
- **Completeness Check:** Fill missing values in `website`, `company`, and `network` columns.

### Phase 4: Validation & Quality Assurance
- **Data Audit:** Ensure no "NULL" values remain in the new required columns.
- **Pricing Cross-Check:** Manually verify MRR for teams with complex agent counts.
- **Metro Accuracy:** Confirm that outlying suburbs are correctly mapped to their respective corporate metros.

### Phase 5: Deep-Dive Research (Strategic Intelligence)
- **Selection:** Identify high-priority teams for intensive research.
- **Process:** Follow the [Deep-Dive Research SOP](team-deep-dive-research.md) to build high-signal profiles, including:
    - Roster & Leadership Structure.
    - Tech Stack & Lead Flow Audit.
    - Strategic Jointly Assessment.

---

## 2. Tools & Scripts

- **Python (Pandas):** For all CSV manipulation and automated calculations.
- **Google Search:** For contact discovery.
- **TREC Background API:** For legal name and roster verification.
- **`enrich_teams_automation.py`**: The master script for Phase 2.
