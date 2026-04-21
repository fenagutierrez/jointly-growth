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
- **Roster Authority:** The live TREC-derived roster from this script is the only authoritative roster for the deep dive. Monthly CSV summaries can be used to screen targets, but must not override the live TREC roster during analysis or documentation.

## Phase 2: Website Identification & Primary Navigation
Before auditing personnel or tech, identify the correct digital home for the brokerage.
- **Identification:** Cross-reference the Designated Broker, DBAs, and Top 5 Producers identified in Phase 1 against Google Search results to isolate the official brokerage website.
- **Mandatory Tooling:** You MUST navigate to the identified website in a live rendered browser session. This is critical for capturing dynamic content, validating what is publicly exposed, and identifying administrative leads that are often hidden from standard scrapers.
- **Rendered-Site Verification:** Confirm that the key pages render correctly in the live browser, including agent/team cards, footer contact details, lead-capture widgets, and any brokerage-wide contact prompts.

## Phase 3: Leadership & Key Personnel Audit
Using the Designated Broker and Top Producers identified in Phase 1, research the brokerage's organizational structure.
- **Identify Key Personnel:** Use the live browser session to explore the brokerage's website and cross-reference with LinkedIn to find:
    - **Office/Operations Manager / Administrative Director:** Key for day-to-day efficiency and tool adoption.
    - **Transaction Coordinator (TC):** Primary user for compliance and form management. Note if the brokerage operates a separate **Transaction Management LLC/Business Unit**.
    - **Financial Accountant:** Key for backend/commission payout automation.
    - **Producing Manager:** High-producing agents (identified in Phase 1) who also hold leadership roles (e.g., "Sales Director"). These are critical influencers who feel the "Squeeze" of managing volume and people simultaneously.
- **Primary Sources (Hierarchy of Truth):**
    1. **Official Brokerage Website:** Use the "Our Team," "Meet the Staff," or "About Us" pages to confirm public-facing roles, titles, and bios.
    2. **LinkedIn (Company Page):** Use to cross-reference current employment status.
- **Verification Mandate:** Do not finalize leadership roles based on search engine snippets alone. You MUST use the live browser session to navigate to the team page and confirm titles.

## Phase 4: Digital Presence & Tech Audit
- **Site Navigation:** Audit the brokerage website identified in Phase 2.
    - **Deep Navigation & Personnel Audit:** Navigate to the "Meet the Team" or "Staff" section. **Capture the full text content of this page** to ensure no administrative leads are missed. Note specific titles like "Operations Manager" vs "Office Admin."
    - **Rendered Contact Audit:** Confirm whether the rendered site publicly exposes direct agent phone numbers, direct emails, office phone numbers, general inboxes, or lead-capture widgets. Record what is actually visible in the browser.
- **Social Media Audit:** Treat social as a required workflow, not a quick stats check.
    - **Step 1: Website-Linked Accounts First:** Start with outbound social links from the official website footer, header, team pages, and contact pages. These are the fastest way to confirm official accounts.
    - **Step 2: Cross-Platform Confirmation:** If one platform links to another official handle (for example, Facebook linking to Instagram), use that to verify the account chain before relying on general web search.
    - **Step 3: Web Search as Fallback:** If a platform is not linked on the website or a confirmed social account, then search the web for the official brokerage presence.
    - **Step 4: Live Rendered Verification:** You MUST inspect `Instagram`, `LinkedIn`, `Facebook`, and `YouTube` in a live rendered browser when possible. Static page fetches are often insufficient for Facebook and Instagram.
    - **Platform Presence:** Confirm which official accounts exist and link them in the profile.
    - **Posting Cadence:** Record whether the account is active in the last 30/90 days and estimate posting frequency.
    - **Audience Size:** Capture follower/subscriber counts when publicly visible.
    - **Content Mix Classification:** Review at least the last `9-12` visible posts and classify the dominant content types: listings, just sold / deal wins, price changes, recruiting / onboarding, agent recognition, market education, legal / compliance education, culture, client testimonials, local/community content, investor content, luxury branding, broker prestige / awards, or team wins.
    - **Primary CTA:** Note the main call to action used in bio/posts: website form, DM, phone call, home-search link, recruiting form, or lead magnet.
    - **Video Maturity:** Identify whether the brand uses reels/short-form video, listing walkthroughs, market updates, podcast clips, or long-form YouTube education.
    - **Paid-Growth Signals:** Note signs of boosted posts, lead-form campaigns, Meta Ad Library activity, or heavy sponsored listing promotion when visible.
    - **Brand Ownership:** Determine whether content appears centrally managed by the brokerage, led by the designated broker/rainmaker, or fragmented across individual agents.
    - **Operational Signal:** Record whether the social presence suggests a polished marketing engine, agent-by-agent DIY marketing, or an inconsistent / low-maintenance digital brand.
    - **Business-Model Interpretation:** Do not stop at follower counts. Explain what the content mix suggests about the brokerage itself: consumer lead-gen shop, recruiting-heavy brokerage, broker-led authority brand, investor-focused operation, luxury-focused brand, or a hybrid model.
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
- **Source Priority Rule:** MLS is the primary contact source. Official website contact information is secondary and should be used to supplement or compare against MLS, not replace it by default.
- **Discrepancy Logging:** If MLS and website contact values conflict, record both values in the profile and explicitly mark MLS as the primary outreach source unless there is a strong documented reason to prefer the website value.
- **Verification Labels:** Label contacts as `MLS-confirmed`, `website-confirmed`, or `needs verification` so the outreach team can quickly assess confidence.

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
    - **Contact Source Labeling:** Every contact entry should identify whether the listed details are `MLS-confirmed`, `website-confirmed`, or `needs verification`.
    - **Contact Discrepancies:** If MLS and website contact values differ, include both in the research notes and clearly indicate which value should be used for primary outreach.
    - **Revenue Share Formulas:** Explicitly state the calculation used for Lease Application and Concierge shares.
    - *Example:* `(Sales Buyer + Lease Tenant) * 0.30 * $42`
- **Timestamp:** Always include the date of the research update at the top.
- **Key Personnel:** Detail bios, roles, LinkedIn links, and verified contact info.
- **Actionable Summary:** Include a clear "Jointly Growth Assessment" section.
