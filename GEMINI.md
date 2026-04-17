# Jointly Growth: Texas Brokerage Intelligence & GTM System

## Project Overview
Jointly Growth is a centralized intelligence hub and automated Go-to-Market (GTM) system designed to identify, research, and convert high-value real estate brokerages in Texas. The project combines deep market research, business strategy, and a Python-powered automation engine to drive growth.

### Core Objectives
*   **Intelligence:** Maintain a comprehensive database of Texas brokerages and teams using TREC and MLS data.
*   **Segmentation:** Identify Ideal Customer Profiles (ICPs) across different tiers (Individual Agents to Enterprise Brokerages).
*   **Automation:** Automate the data pipeline from raw licensing dumps to enriched prospecting profiles and synchronized CRM data.

---

## Directory Structure & Key Components

### 📂 `00.companies/`
The data repository for brokerage and team intelligence.
*   **`brokerages/`**: Contains monthly TREC data, processed summaries, and detailed target profiles (Tier 1 to Tier 3).
*   **`teams/`**: Data and profiles for Texas real estate teams.
*   **`process-documentation/`**: Standard Operating Procedures (SOPs) for data processing and research.

### 📂 `01.strategy/`
The strategic brain of the growth operation.
*   **`comprehensive-icp-map.md`**: Defines target segments (Agents, Teams, Boutiques, Enterprise).
*   **`marketing-plan-2026.md`**: Current year growth roadmap.
*   **`tier-3-assets/`**: Specific resources for the boutique brokerage segment (Rev-share calculators, ROI accelerators).

### 📂 `02.competitor-analysis/`
Deep-dive research into industry incumbents like Dotloop and Paperless Pipeline.

### 📂 `03.proposals/`
Active sales proposals and pitch decks for high-priority targets.

### 📂 `04.dev/`
The automation engine supporting the research and sales motions.
*   **`src/data/`**: PostgreSQL database connection logic (`db_conn.py`) and SQL queries.
*   **`src/config/`**: Synchronization configurations for Intercom, Chameleon, and lead generation tools.
*   **`src/utils/`**: Helper utilities, including Google Sheets integration.
*   **`scripts/`**: Operational scripts for brokerage deep-dives (`brokerage_deep_dive.py`), production analysis, and contact enrichment.

---

## Tech Stack & Architecture

### 🛠️ Core Technologies
*   **Language:** Python 3.x
*   **Data Processing:** `pandas` for handling CSV summaries and MLS/TREC data.
*   **Database:** PostgreSQL (accessed via `psycopg2`).
*   **APIs:** TREC API, Sentry, Intercom, Chameleon, MLS Choice.
*   **Integrations:** Google Sheets (for shared tracking), Airtable (for CRM-like data).

### ⚙️ Development Conventions
*   **Configuration & Secrets:** 
    *   System configuration is managed in `04.dev/config/config.py`.
    *   Sensitive credentials (DB, APIs) are stored in `.ini` files within `04.dev/secrets/` (e.g., `database.ini`, `api.ini`).
    *   **NEVER** commit files in the `secrets/` directory.
*   **Modularity:** 
    *   Shared logic should reside in `04.dev/src/utils/`.
    *   Database queries should be centralized in `04.dev/src/data/sql_queries.py`.
*   **Data Flow:** Raw data is typically ingested into `00.companies/brokerages/source/`, processed via scripts in `04.dev/scripts/`, and output to `00.companies/brokerages/output/summaries/`.

---

## Getting Started

### 📋 Prerequisites
*   Python 3.x
*   PostgreSQL access
*   Valid `.ini` configuration files in `04.dev/secrets/` (use `api.ini.example` as a template).

### 🚀 Common Commands
*   **Enrich Brokerage Data:** 
    `python 04.dev/scripts/enrich_top_100_production.py`
*   **Run Brokerage Deep-Dive:** 
    `python 04.dev/scripts/brokerage_deep_dive.py`
*   **Sync User Data:** 
    (Inferred) Scripts in `04.dev/scripts/` or `04.dev/src/` are used to sync with external platforms like Intercom.

---

## Reference Documents
*   **Business Pricing:** `00.companies/brokerages/process-documentation/pricing-structure.md`
*   **Profile Template:** `00.companies/brokerages/process-documentation/templates/template.md`
*   **TREC Data SOP:** `00.companies/brokerages/process-documentation/trec-data-processing/TREC_data_process.md`
