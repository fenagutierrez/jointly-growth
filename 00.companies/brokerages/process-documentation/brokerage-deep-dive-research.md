# SOP: Brokerage Deep-Dive Research

This document defines the systematic process for researching a brokerage to build a high-signal prospect profile for Jointly's growth team. 

**Important:** Do not skip any steps, and go through this in order.

## Phase 1: Automated Discovery & Production Analysis
The first step is to run the automated deep-dive script to instantly gather licensing data, the agent roster, and 12-month production metrics.
- **Action:** Run the `brokerage_deep_dive.py` script located in `04.dev/scripts/`.
    ```bash
    cd 04.dev/
    .venv/bin/python3 scripts/brokerage_deep_dive.py "[BROKER-LICENSE-BB]"
    ```
- **Outcomes:** 
    - Identifies DBAs and Team Names.
    - Identifies the Designated Broker.
    - Extracts the full sponsored agent roster (including the Designated Broker) directly from TREC.
    - Queries the MLS database for 12-month production (Units/Volume for Sales and Leases).
    - Calculates brokerage seat count and **MRR Potential** using the Jointly Business pricing model.
    - Calculates estimated Brokerage GCI and potential Jointly Revenue Share.
    - Identifies the Top 5 Sales and Lease Producers.

## Phase 2: Website Identification & Primary Navigation
Before auditing personnel or tech, identify the correct digital home for the brokerage.
- **Identification:** Cross-reference the Designated Broker, DBAs, and Top 5 Producers identified in Phase 1 against Google Search results to isolate the official brokerage website.
- **Mandatory Tooling:** You MUST navigate to the identified website using **MCP Playwright** (`browser_navigate`). This is critical for capturing dynamic content and identifying administrative leads that are often hidden from standard scrapers.

## Phase 3: Leadership & Key Personnel Audit
Using the Designated Broker and Top Producers identified in Phase 1, research the brokerage's organizational structure.
- **Identify Key Personnel:** Use the Playwright session to explore the brokerage's website and cross-reference with LinkedIn to find:
    - **Office/Operations Manager / Administrative Director:** Key for day-to-day efficiency and tool adoption.
    - **Transaction Coordinator (TC):** Primary user for compliance and form management. Note if the brokerage operates a separate **Transaction Management LLC/Business Unit**.
    - **Financial Accountant:** Key for backend/commission payout automation.
    - **Producing Manager:** High-producing agents (identified in Phase 1) who also hold leadership roles (e.g., "Sales Director"). These are critical influencers who feel the "Squeeze" of managing volume and people simultaneously.
- **Primary Sources (Hierarchy of Truth):**
    1. **Official Brokerage Website:** Always prioritize the "Our Team," "Meet the Staff," or "About Us" pages. This is the **Primary Source of Truth**.
    2. **LinkedIn (Company Page):** Use to cross-reference current employment status.
- **Verification Mandate:** Do not finalize leadership roles based on search engine snippets alone. You MUST use Playwright to navigate to the team page and confirm titles.

## Phase 4: Digital Presence & Tech Audit
- **Site Navigation:** Audit the brokerage website identified in Phase 2.
    - **Deep Navigation & Personnel Audit:** Navigate to the "Meet the Team" or "Staff" section. **Capture the full text content of this page** to ensure no administrative leads are missed. Note specific titles like "Operations Manager" vs "Office Admin."
- **Social Media Presence:** Audit platforms (Instagram, LinkedIn, Facebook) for activity, follower count, and content strategy.
    - **YouTube:** Identify video-led education, market updates, or agent recruitment videos.
- **Tech Stack Identification:** Identify the platform provider (e.g., Luxury Presence, Pipeline ROI, Propertybase, Chime) from the footer or source.
- **Identify Friction Points:** Look for "Legacy Tech" signals:
    - "Download Adobe Acrobat" or PDF viewer links.
    - Static PDF rental applications or forms.
    - Non-mobile-responsive UI.
    - Generic iframe-based MLS search portals (e.g., Buying Buddy).
- **Brand Extraction:** Identify the company slogan and "Core Promises" to align with Jointly's value proposition.

## Phase 5: Contact Extraction (Automated)
- **Contact Extraction:** Use the `get_agent_contacts.py` script to retrieve verified emails and phone numbers from the MLS database for the Designated Broker, Top Producers, and identified Leadership.
    - Update the `target_lics` and `target_names` lists within the script before running.
    ```bash
    .venv/bin/python3 scripts/get_agent_contacts.py
    ```
- **Script Capabilities:**
    - **Contact Retrieval:** Pulls `listing_agent_email` and `listing_agent_phone` directly from the `mls.member` table.

## Phase 6: Jointly Strategic Assessment
- **Strategic Interpretation:** Review the "Growth Profile Summary" output from Phase 1.
    - **Units vs. Sides:** Confirm the brokerage's business mix (Sales vs. Leases).
    - **MRR Potential:** Estimate the monthly software value of the full brokerage roster based on seat count.
    - **Benchmark:** Minimum GCI of $200,000/year for software investment justification.
- **ICP Mapping:** Classify the brokerage based on the [Comprehensive ICP Map](../../../01.strategy/comprehensive-icp-map.md) (e.g., Tier 1 "High-Volume Independent").
- **Pain Point Alignment:** 
    - **Lease Complexity:** High-volume lease operations (e.g., >100/year) are prime for Jointly.
    - **Producing Manager Relief:** Focus on "Buying Back Time" for leadership who still sell.
    - **Administrative Director Efficiency:** Target operations leads with the "Unified Compliance" angle.
- **Sales Motion Recommendation:**
    - **Katarina AI:** Automated efficiency outreach to Top 5 Producers (using extracted email/phone).
    - **Devin-led:** High-touch executive pitch for complex needs or tech consolidation.
    - **HAR/Unlock Subsidies:** Leverage association partnerships for "Net-Zero" profitability.

## Phase 7: Documentation
- **Profile Creation:** Create or update the brokerage markdown profile in `00.companies/brokerages/profiles/profiles-tier-1/` or `00.companies/brokerages/profiles/profiles-tier-3/`.
- **Template Structure:** Use `00.companies/brokerages/process-documentation/templates/template.md`.
- **Mandatory Production & Contact Details:**
    - **MRR:** Always include the estimated monthly subscription value based on the brokerage's full analyzed roster size.
    - **Side Distributions:** Always specify the breakdown (e.g., "54 Buyer / 39 Listing") for both Sales and Leases from the Phase 1 script output.
    - **Contact Information:** EVERY key personnel and top producer entry MUST include an email and phone number.
    - **Revenue Share Formulas:** Explicitly state the calculation used for Lease Application and Concierge shares.
        - *Example:* `(Sales Buyer + Lease Tenant) * 0.30 * $42`
- **Timestamp:** Always include the date of the research update at the top.
- **Key Personnel:** Detail bios, roles, LinkedIn links, and verified contact info.
- **Actionable Summary:** Include a clear "Jointly Growth Assessment" section.
