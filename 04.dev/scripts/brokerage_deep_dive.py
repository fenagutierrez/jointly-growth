#!/usr/bin/env python3
"""
Brokerage Deep-Dive Research Script
Automates the extraction of agent rosters, queries production data from the MLS database,
and generates a Growth Profile Summary.
"""

import sys
import pandas as pd
import json
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Any

# Add project root to sys.path
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.absolute()
sys.path.insert(0, str(project_root))

from src.data.db_conn import load_db_table
from src.data.sql_queries import get_mls_roster_production_query
from src.utils.output import (
    build_analysis_payload,
    build_entity_metadata,
    print_analysis_summary,
    print_json_payload,
)
from src.utils.production_analysis import analyze_roster_production
from src.utils.roster import normalize_license, normalize_license_list, normalize_roster

def fetch_trec_data(license_number):
    """Fetches full details including DBA, Team Names, Designated Broker, and Sales Agents."""
    url = f"https://www.trec.texas.gov/acaif/api/licenseDetail/{license_number}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
    }
    
    result = {
        "dbas": [],
        "teams": [],
        "designated_broker": "None",
        "sales_agents": []
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                detail = data[0]
                result["dbas"] = detail.get("dbas", [])
                result["teams"] = detail.get("teamNames", [])
                
                sponsoring = detail.get("sponsoringData", [])
                sponsored_licenses = []
                if isinstance(sponsoring, dict):
                    sponsored_licenses = [v["sponsorLicenseNumber"] for v in sponsoring.values() if isinstance(v, dict) and "sponsorLicenseNumber" in v]
                elif isinstance(sponsoring, list):
                    sponsored_licenses = [v["sponsorLicenseNumber"] for v in sponsoring if isinstance(v, dict) and "sponsorLicenseNumber" in v]
                
                for i, lic in enumerate(sponsored_licenses, 1):
                        # Fetch detail for each sponsored license to get Name and Type
                        agent_url = f"https://www.trec.texas.gov/acaif/api/licenseDetail/{lic}"
                        agent_resp = requests.get(agent_url, headers=headers, timeout=5)
                        if agent_resp.status_code == 200:
                            agent_data = agent_resp.json()
                            if isinstance(agent_data, list) and len(agent_data) > 0:
                                agent_detail = agent_data[0]
                                name = f"{agent_detail.get('firstName', '')} {agent_detail.get('lastName', '')}".strip()
                                lic_type = agent_detail.get("type", "")
                                
                                if "Broker" in lic_type:
                                    result["designated_broker"] = f"{name} ({lic})"
                                else:
                                    result["sales_agents"].append(f"{name} ({lic})")
                        
    except Exception as e:
        print(f"Error fetching {license_number}: {e}")
    
    return result

def get_production_data(agent_licenses: List[str], config_db: str = "janet.ini") -> pd.DataFrame:
    """Queries production data for the last 12 months."""
    if not agent_licenses:
        return pd.DataFrame()
    
    # Clean licenses
    cleaned = [f"'{lic}'" for lic in normalize_license_list(agent_licenses)]
            
    licenses_str = ", ".join(cleaned)
    
    query = get_mls_roster_production_query(licenses_str)
    return load_db_table(config_db, query)

def process_production(df: pd.DataFrame, roster: Dict[str, str]) -> Dict[str, Any]:
    """Calculates GCI, Top Producers, Revenue Shares, and MRR potential."""
    return analyze_roster_production(df, roster)

def main():
    parser = argparse.ArgumentParser(description="Analyze brokerage production based on broker license.")
    parser.add_argument("broker_license", type=str, help="Broker company license number.")
    parser.add_argument("--config", type=str, default="janet.ini", help="Database config file.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")

    args = parser.parse_args()
    broker_license = args.broker_license
    
    print(f"--- Researching Brokerage: {broker_license} ---")
    
    print("Step 1: Fetching TREC License Details (API)...")
    trec_data = fetch_trec_data(broker_license)
    dbas = ", ".join(trec_data.get("dbas", []))
    teams = ", ".join(trec_data.get("teams", []))
    broker = trec_data.get("designated_broker", "None")
    agents = trec_data.get("sales_agents", [])

    if dbas:
        print(f"  - DBAs Identified: {dbas}")
    if teams:
        print(f"  - Team Names Identified: {teams}")
    if broker != "None":
        print(f"  - Designated Broker: {broker}")
    
    print("Step 2: Building Agent Roster...")
    roster = {}
    
    # Add Designated Broker to roster
    if broker != "None" and " (" in broker:
        name, lic = broker.rsplit(" (", 1)
        lic = lic.rstrip(")")
        clean_lic = normalize_license(lic)
        roster[clean_lic] = name
    
    # Add Sponsored Agents to roster
    for agent_str in agents:
        if " (" in agent_str:
            name, lic = agent_str.rsplit(" (", 1)
            lic = lic.rstrip(")")
            clean_lic = normalize_license(lic)
            roster[clean_lic] = name

    roster, roster_warnings = normalize_roster(roster)
    print(f"Found {len(roster)} agents (including Designated Broker).")
    
    if not roster:
        print("No agents found. Exiting.")
        return
        
    print("Step 3: Querying Production Database (Last 12 Months)...")
    licenses = list(roster.keys())
    df = get_production_data(licenses, args.config)
    print(f"Retrieved {len(df)} transaction sides.")
    
    print("Step 4: Processing Production Data...")
    analysis = process_production(df, roster)
    
    payload = build_analysis_payload(
        entity_type="brokerage",
        entity_name=dbas.split(",")[0].strip() or broker_license,
        roster=roster,
        analysis=analysis,
        warnings=roster_warnings,
        metadata=build_entity_metadata(
            entity_id=broker_license,
            entity_type="brokerage",
            primary_contact_name=broker if broker != "None" else None,
            primary_license=broker_license,
            website=None,
            brand_names=trec_data.get("dbas", []),
            brokerage_affiliation=None,
            source="trec_api",
            config=args.config,
            extra={
                "team_names": trec_data.get("teams", []),
                "designated_broker": broker,
            },
        ),
    )

    if args.json:
        print_json_payload(payload)
        return

    print_analysis_summary("GROWTH PROFILE SUMMARY", payload, "Brokerage")

if __name__ == "__main__":
    main()
