# SOP: Texas Real Estate Team Deep-Dive Research

This document defines the intensive research process for high-priority real estate teams, expanding beyond basic enrichment into strategic intelligence.

## 1. Process Overview

### Phase 0: The Anchor URL (Mandatory Start)
- **Primary Source Identification:** Every deep-dive MUST start with the team's official website URL. 
- **URL Discovery:** If the URL is missing from the baseline CSV, use Google Search (e.g., `"[Team Name]" [City] Texas Real Estate Team`) to locate it.
- **Geographic Validation:** Validate the URL against the target market. If the website footer lists out-of-state licenses (e.g., Florida SL/BK) but we are targeting Texas, search for the specific "Texas Unit" landing page or sub-domain (e.g., `emeraldinvestsatx.com`).
- **Reliability:** The official website is the **Primary Source of Truth** for roster size, leadership roles, and tech stack signals. 

### Phase 1: Roster Identification & License Extraction
- **Full Roster Audit:** Identify all team members listed on the "Our Team" or "About" pages. This is the primary source of truth for seat count and roles.
- **License Extraction:** If the website displays TREC license numbers (e.g., "License #700093"), extract them for every member. These are critical unique identifiers for automation.
- **Team Lead Profile:** Verify the primary licensee.
    - **TREC Check:** Confirm license status and primary brokerage affiliation.
    - **Experience:** Note years in the industry and specialization (e.g., Luxury, Multi-family, REO).
- **Operations & Support:** Identify the "Engine" of the team:
    - **Workflow Ownership:** Identify the true daily user of the transaction stack. Look for "Operations Coordinator," "Client Care," or "Director of Operations" in site widgets or "About" pages.
- **Verification Mandate:** Do not rely solely on third-party counts (e.g., RealTrends). Always use the official website's roster as the baseline.

### Phase 2: Production & Contact Intelligence (Automated)
Once the roster and licenses are identified, execute automated intelligence gathering:
- **Production Deep-Dive:** Run `team_deep_dive.py` using the extracted license numbers.
    - **Outcome:** The script automatically calculates:
        - Total sides and GCI distribution.
        - Lease vs. Sales ratios.
        - **MRR Potential:** Precise monthly subscription estimates based on seat count.
        - **Revenue Share Opportunity:** Jointly's potential share from leases and concierge services.
- **Contact Enrichment:** Run `get_agent_contacts.py` for key roster members.
    - **Goal:** Locate direct professional emails or cell phone numbers that are often bypassed by generic website contact forms.
- **Validation:** Cross-reference MLS emails with team domains to confirm the high-priority target addresses.

### Phase 3: Tech Stack & Lead Flow Audit
- **CRM & Marketing Platform:** Identify the core system (e.g., KVCore, Lofty, Follow Up Boss).
    - *Signal:* Look for site footers or login subdomains (e.g., `leads.teamname.com`).
- **Lead Generation Sources:** Identify how they generate volume:
    - **Zillow/Realtor.com:** High-spend teams are prime candidates for Jointly.
    - **PPC/Google Ads:** Note heavy digital marketing presence.
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

---

## 2. Tools & Resources

- **Primary Search:** Google Search, LinkedIn, Official Team Websites.
- **Verification:** TREC (Texas Real Estate Commission) License Lookup.
- **Scripts:**
    - `04.dev/scripts/team_deep_dive.py` (Full Production & MRR Analysis)
    - `04.dev/scripts/get_agent_contacts.py` (Contact Enrichment)
