# SOP: Texas Real Estate Team Deep-Dive Research

This document defines the intensive research process for high-priority real estate teams, expanding beyond basic enrichment into strategic intelligence.

## 1. Process Overview

### Phase 0: The Anchor URL (Mandatory Start)
- **Primary Source Identification:** Every deep-dive MUST start with the team's official website URL. 
- **URL Discovery:** If the URL is missing from the baseline CSV, use Google Search (e.g., `"[Team Name]" [City] Texas Real Estate Team`) to locate it.
- **Geographic Validation:** Validate the URL against the target market. If the website footer lists out-of-state licenses (e.g., Florida SL/BK) but we are targeting Texas, search for the specific "Texas Unit" landing page or sub-domain (e.g., `emeraldinvestsatx.com`).
- **Reliability:** The official website is the **Primary Source of Truth** for roster size, leadership roles, and tech stack signals. 

### Phase 1: Roster Identification & TREC License Verification
- **Full Roster Audit:** Identify all team members listed on the "Our Team" or "About" pages. The official website is the primary source of truth for the **team roster**, seat count, leadership roles, and support roles.
- **Brokerage License Discovery (TREC-First):** Before relying on MLS/member data for licenses, identify the team's sponsoring broker company license.
    - Start with any license or brokerage information shown on the official website, TREC notices, IABS documents, footer disclosures, agent pages, or listing pages.
    - Search the monthly TREC CSV for the team lead, brokerage DBA, and visible agent names if the broker company license is not obvious.
    - Confirm the broker company through TREC API detail data. The broker company should have DBAs, team names, or sponsored agents that plausibly match the team. For larger franchise offices, the broker company roster may include many non-team agents; do not treat the full brokerage roster as the team roster.
    - **License Type Check:** When a license number is displayed on the team website, verify its *type* in TREC before treating it as a personal license. A displayed number may be a Broker Company license (e.g., the franchise's company license), a Broker Individual license, or a Sales Agent license — each has different implications for the roster analysis.
    - **Broker Individual Under Franchise:** If the team lead holds a Broker Individual license and works under a franchise umbrella (e.g., Compass, KW), they will NOT appear as a sponsored agent under the franchise's Broker Company license. Searching the franchise's sponsored roster will not surface them. Confirm their individual license separately via TREC name search or CSV match.
- **TREC Brokerage Roster Pull:** Once the broker company license is confirmed, fetch the TREC license detail for that broker company using the TREC API or an existing helper such as `fetch_trec_details.py`.
    - Capture DBAs, team names, designated broker if available, and sponsored licensees.
    - Confirm that the relevant team name appears in `teamNames` when available (for example, "THE [TEAM NAME] GROUP"). If it does not, document the reason the brokerage is still believed to be correct.
- **Secondary Roster Source — Franchise/Brokerage Team Page:** If the team is affiliated with a franchise (e.g., Compass, KW, RE/MAX), check the franchise's own agent team page (e.g., `compass.com/agents/[team-slug]/`) alongside the official team website. These pages can surface members the official website omits, or reveal former members who have departed but whose franchise profile has not been updated. Cross-check both sources and flag discrepancies.
- **Roster-to-TREC Matching:** Match the official website roster against the TREC-sponsored roster to assign licenses.
    - Use exact name matches first, then conservative normalized/fuzzy matching for common variants (e.g., James Michael Tash vs. Michael Tash, Carl Clayton Jones vs. Clayton Jones).
    - Keep inactive, out-of-state, duplicate, or unrelated name matches out of the production roster unless there is strong corroboration.
    - If an official roster member is not found under the confirmed broker company, search TREC directly by name and document whether they are licensed under a different broker, inactive, support-only, or unverified.
    - If the official website displays a TREC license number, still confirm the license status and sponsoring broker in TREC.
    - **Expired Licenses on Active Websites:** If a team member's TREC license is expired but they are still listed on the team website, exclude them from the production roster and flag this explicitly in the profile. A pattern of multiple expired or departed members is a team stability signal worth noting in the strategic assessment.
    - **Unlicensed Contractors with Agent-Like Titles:** Team websites sometimes list photographers, marketers, or TC staff with titles like "REALTOR®" or "Agent." If a roster member cannot be matched to any active TREC record, document them as an unverified/support role rather than a production seat.
- **Team Lead Profile:** Verify the primary licensee in TREC.
    - **TREC Check:** Confirm license status and sponsoring broker affiliation.
    - **Experience:** Note years in the industry and specialization (e.g., Luxury, Multi-family, REO, Farm & Ranch).
- **Operations & Support:** Identify the "Engine" of the team:
    - **Workflow Ownership:** Identify the true daily user of the transaction stack. Look for "Operations Coordinator," "Client Care," "Listing Coordinator," "Experience Director," or "Director of Operations" in site widgets or "About" pages.
    - Support/ops staff may not appear in TREC and should be counted separately from licensed production seats.
- **Verification Mandate:** Do not rely solely on third-party counts (e.g., RealTrends) or MLS/member lookup. Always use the official website as the team roster baseline and TREC as the authoritative source for license status and brokerage affiliation.

### Phase 2: Production & Contact Intelligence (Automated)
Once the official roster has been matched to TREC-verified licenses, execute automated intelligence gathering:
- **Production Deep-Dive:** Run `team_deep_dive.py` using only the TREC-verified licensed team roster.
    - **Outcome:** The script automatically calculates:
        - Total sides and GCI distribution.
        - Lease vs. Sales ratios.
        - **MRR Potential:** Precise monthly subscription estimates based on seat count.
        - **Revenue Share Opportunity:** Jointly's potential share from leases and concierge services.
- **Contact Enrichment:** Run `get_agent_contacts.py` for key roster members.
    - **Goal:** Locate direct professional emails or cell phone numbers that are often bypassed by generic website contact forms.
- **Validation:** Cross-reference MLS emails with team domains to confirm the high-priority target addresses. MLS/member data is a contact and production enrichment layer, not the primary license/brokerage authority.

### Phase 3: Tech Stack & Lead Flow Audit
- **CRM & Marketing Platform:** Identify the core system (e.g., KVCore, Lofty, Follow Up Boss).
    - *Signal:* Look for site footers or login subdomains (e.g., `leads.teamname.com`).
- **Lead Generation Sources:** Identify how they generate volume:
    - **Zillow/Realtor.com:** High-spend teams are prime candidates for Jointly.
    - **PPC/Google Ads:** Note heavy digital marketing presence.
- **Social Media Audit:** Treat social as a required workflow, not a quick stats check.
    - **Step 1: Website-Linked Accounts First:** Start with outbound social links from the official website footer, header, agent pages, and contact pages. These are the fastest way to confirm official accounts.
    - **Step 2: Cross-Platform Confirmation:** If one platform links to another official handle (for example, Facebook linking to Instagram), use that to verify the account chain before relying on general web search.
    - **Step 3: Web Search as Fallback:** If a platform is not linked on the website or a confirmed social account, then search the web for the official team presence.
    - **Step 4: Live Rendered Verification:** You MUST inspect `Instagram`, `LinkedIn`, `Facebook`, and `YouTube` in a live rendered browser when possible. Static page fetches are often insufficient for Facebook and Instagram.
    - **Platform Presence:** Confirm which official accounts exist and link them in the profile.
    - **Posting Cadence:** Record whether the account is active in the last 30/90 days and estimate posting frequency.
    - **Audience Size:** Capture follower/subscriber counts when publicly visible.
    - **Content Mix Classification:** Review at least the last `9-12` visible posts and classify the dominant content types: listings, just sold / deal wins, price changes, recruiting / onboarding, agent recognition, market education, legal / compliance education, culture, client testimonials, local/community content, investor content, luxury branding, broker prestige / awards, or team wins.
    - **Primary CTA:** Note the main call to action used in bio/posts: website form, DM, phone call, home-search link, recruiting form, or lead magnet.
    - **Video Maturity:** Identify whether the brand uses reels/short-form video, listing walkthroughs, market updates, podcast clips, or long-form YouTube education.
    - **Paid-Growth Signals:** Note signs of boosted posts, lead-form campaigns, Meta Ad Library activity, or heavy sponsored listing promotion when visible.
    - **Brand Ownership:** Determine whether content appears centrally managed by the team, led by the rainmaker, or fragmented across individual agents.
    - **Operational Signal:** Record whether the social presence suggests a polished marketing engine, agent-by-agent DIY marketing, or an inconsistent / low-maintenance digital brand.
    - **Business-Model Interpretation:** Do not stop at follower counts. Explain what the content mix suggests about the team itself: consumer lead-gen team, recruiting-heavy expansion team, rainmaker-led authority brand, investor-focused operation, luxury-focused brand, or a hybrid model.
- **Form Usage & Friction:**
    - Do they offer digital disclosures or use static PDFs?
    - Is there a "Join Our Team" or "Recruiting" page?

### Phase 4: Jointly Strategic Assessment
- **Business Model Segmentation:** Categorize the team's primary driver (Investor, Luxury, Relocation, etc.).
- **Value Proposition Mapping:**
    - **For the Rainmaker:** Focus on visibility and "Buying Back Time."
    - **For the Workflow Owner (Ops):** Focus on compliance automation and reducing TC overhead.
    - **For the Agent:** Focus on "Mobile-First" deal management.
- **Competitive Positioning:** How does Jointly complement or replace their current stack?

### Phase 5: Documentation
- **Profile Creation (Mandatory):** ALWAYS create a dedicated markdown profile in `00.companies/teams/profiles/[team-slug].md`. 
    - **Do NOT update the master CSV** for deep-dive intelligence; the CSV is for baseline outreach.
- **Template Usage:** Use the [Team Profile Template](templates/team-profile-template.md) for all new entries.
- **Timestamp:** Always include the date of the research update at the top of the profile.
- **Google Drive Upload (Mandatory):** After creating or updating the local markdown profile, upload it to the shared Google Drive profiles folder using the `gws` CLI:
    - **New profile:** `gws drive files create --json '{"name": "[Team Name]", "mimeType": "application/vnd.google-apps.document", "parents": ["1pzNMdOPG1-UT1htatBs90a73g84Cx5-1"]}' --upload 00.companies/teams/profiles/[team-slug].md --upload-content-type text/plain`
    - **Update existing:** First find the file ID with `gws drive files list --params '{"q": "\"1pzNMdOPG1-UT1htatBs90a73g84Cx5-1\" in parents and trashed = false", "fields": "files(id,name)"}'`, then: `gws drive files update --params '{"fileId": "[FILE_ID]"}' --upload 00.companies/teams/profiles/[team-slug].md --upload-content-type text/plain`
    - **Profiles Folder:** https://drive.google.com/drive/folders/1pzNMdOPG1-UT1htatBs90a73g84Cx5-1
- **Spreadsheet Link Update (Mandatory):** After uploading, record the Google Doc link in the master spreadsheet (`medium_teams_texas` sheet, `profile link` column):
    1. Find the team's row: search column A for the team name.
    2. Write the Google Doc URL to column C of that row:
       `gws sheets spreadsheets values update --params '{"spreadsheetId": "1T8taDH4WPC47R2YSlPdXavFlX6kvmvZamhy1NPBIQOA", "range": "medium_teams_texas!C[ROW]", "valueInputOption": "USER_ENTERED"}' --json '{"values": [["https://docs.google.com/document/d/[FILE_ID]/edit"]]}'`
    - **Spreadsheet:** https://docs.google.com/spreadsheets/d/1T8taDH4WPC47R2YSlPdXavFlX6kvmvZamhy1NPBIQOA/edit

---

## 2. Tools & Resources

- **Primary Search:** Google Search, LinkedIn, Official Team Websites.
- **Verification:** TREC (Texas Real Estate Commission) License Lookup and TREC broker company detail API.
- **Scripts:**
    - `04.dev/scripts/fetch_trec_details.py` (Broker company DBA/team/sponsored-agent verification)
    - `04.dev/scripts/team_deep_dive.py` (Full Production & MRR Analysis)
    - `04.dev/scripts/get_agent_contacts.py` (MLS-based Contact Enrichment, after TREC verification)
- **Local TREC Source:**
    - `00.companies/brokerages/source/trec/Broker_and_Sales_Agent_License_Holder_Information_YYYYMMDD.csv` (Monthly TREC snapshot for broker/license discovery and fallback matching)
