#!/usr/bin/env python3
"""
Team Deep-Dive Research Script
Queries production data for a specific set of agent licenses (team roster) 
and calculates GCI and growth potential.
"""

import sys
import pandas as pd
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Add project root to sys.path
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.absolute()
sys.path.insert(0, str(project_root))

from src.data.db_conn import load_db_table
from src.data.sql_queries import get_mls_roster_production_query
from src.utils.entity_input import load_entity_input, merge_entity_input
from src.utils.output import (
    build_analysis_payload,
    build_entity_metadata,
    print_analysis_summary,
    print_json_payload,
)
from src.utils.production_analysis import analyze_roster_production
from src.utils.roster import normalize_license_list, normalize_roster

def get_production_data(agent_licenses: List[str], config_db: str = "janet.ini") -> pd.DataFrame:
    """Queries production data for the last 12 months for a list of licenses."""
    if not agent_licenses:
        return pd.DataFrame()
    
    # Clean licenses
    cleaned = [f"'{lic}'" for lic in normalize_license_list(agent_licenses)]
            
    if not cleaned:
        return pd.DataFrame()
            
    licenses_str = ", ".join(cleaned)
    
    query = get_mls_roster_production_query(licenses_str)
    return load_db_table(config_db, query)

def process_production(df: pd.DataFrame, roster: Dict[str, str]) -> Dict[str, Any]:
    """Calculates GCI, Top Producers, Revenue Shares, and MRR potential."""
    return analyze_roster_production(df, roster)


def main():
    parser = argparse.ArgumentParser(description="Analyze team production based on agent licenses.")
    parser.add_argument("--licenses", type=str, help="Comma-separated list of agent licenses.")
    parser.add_argument("--roster_file", type=str, help="Path to a JSON file containing {license: name} mapping.")
    parser.add_argument("--entity-file", type=str, help="Path to a JSON file containing team metadata.")
    parser.add_argument("--team-name", type=str, help="Team name.")
    parser.add_argument("--team-lead-name", type=str, help="Primary team lead name.")
    parser.add_argument("--team-lead-license", type=str, help="Primary team lead license.")
    parser.add_argument("--website", type=str, help="Official team website.")
    parser.add_argument("--brokerage-affiliation", type=str, help="Brokerage affiliation.")
    parser.add_argument("--brand-name", dest="brand_names", action="append", default=None, help="Brand or DBA name. Repeatable.")
    parser.add_argument("--source", type=str, help="Metadata source label.")
    parser.add_argument("--config", type=str, default="janet.ini", help="Database config file.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON output.")
    
    args = parser.parse_args()
    
    roster = {}
    if args.roster_file:
        with open(args.roster_file, 'r') as f:
            roster = json.load(f)
    elif args.licenses:
        # Create a dummy roster from licenses if names are unknown
        lic_list = [l.strip() for l in args.licenses.split(",")]
        for l in lic_list:
            roster[l] = f"Agent {l}"
    else:
        print("Error: Either --licenses or --roster_file must be provided.")
        sys.exit(1)

    roster, roster_warnings = normalize_roster(roster)
    entity_file_data = load_entity_input(args.entity_file)
    entity_input = merge_entity_input(
        entity_file_data,
        {
            "team_name": args.team_name,
            "team_lead_name": args.team_lead_name,
            "team_lead_license": args.team_lead_license,
            "website": args.website,
            "brokerage_affiliation": args.brokerage_affiliation,
            "brand_names": args.brand_names,
            "source": args.source,
        },
    )
    print(f"--- Analyzing Team Production for {len(roster)} Seats ---")
    
    licenses = list(roster.keys())
    df = get_production_data(licenses, args.config)
    print(f"Retrieved {len(df)} transaction sides for the last 12 months.")
    
    analysis = process_production(df, roster)
    if not analysis:
        print("No production data found for these licenses.")
        return

    payload = build_analysis_payload(
        entity_type="team",
        entity_name=entity_input.get("team_name", "Team Roster Analysis"),
        roster=roster,
        analysis=analysis,
        warnings=roster_warnings,
        metadata=build_entity_metadata(
            entity_id=entity_input.get("team_lead_license"),
            entity_type="team",
            primary_contact_name=entity_input.get("team_lead_name"),
            primary_license=entity_input.get("team_lead_license"),
            website=entity_input.get("website"),
            brand_names=entity_input.get("brand_names", []),
            brokerage_affiliation=entity_input.get("brokerage_affiliation"),
            source=entity_input.get("source", "manual_roster_input"),
            config=args.config,
            extra={"team_name": entity_input.get("team_name")},
        ),
    )

    if args.json:
        print_json_payload(payload)
        return

    print_analysis_summary("TEAM GROWTH PROFILE SUMMARY", payload, "Team")

if __name__ == "__main__":
    main()
