#!/usr/bin/env python3
"""
Brokerage Deep-Dive Research Script
Automates the extraction of agent rosters, queries production data from the MLS database,
and generates a Growth Profile Summary.
"""

import sys
import pandas as pd
import json
import requests
from pathlib import Path
from typing import List, Dict, Any

# Add project root to sys.path
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.absolute()
sys.path.insert(0, str(project_root))

from src.data.db_conn import load_db_table
from src.utils.pricing import calculate_jointly_business_mrr

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
    cleaned = []
    for lic in agent_licenses:
        c = ''.join(filter(str.isdigit, str(lic))).lstrip('0')
        if c:
            cleaned.append(f"'{c}'")
            
    licenses_str = ", ".join(cleaned)
    
    query = f"""
    WITH BaseProperties AS (
        SELECT
            p.list_agent_full_name AS la_name,
            COALESCE(p.listing_agent_email, la.listing_agent_email) AS la_email,
            COALESCE(
                NULLIF(LTRIM(REGEXP_REPLACE(p.listing_agent_state_license, '[^0-9]', '', 'g'), '0'), ''),
                NULLIF(LTRIM(REGEXP_REPLACE(la.mls_id, '[^0-9]', '', 'g'), '0'), '')
            ) AS la_license_number,
            p.buyer_agent_full_name AS ba_name,
            COALESCE(p.buyer_agent_email, ba.listing_agent_email) AS ba_email,
            COALESCE(
                NULLIF(LTRIM(REGEXP_REPLACE(p.buyer_agent_state_license, '[^0-9]', '', 'g'), '0'), ''),
                NULLIF(LTRIM(REGEXP_REPLACE(ba.mls_id, '[^0-9]', '', 'g'), '0'), '')
            ) AS ba_license_number,
            p.list_price / 100.0 AS list_price,
            p.close_price / 100.0 AS close_price,
            p.property_type,
            p.close_date,
            p.address
        FROM mls.property p
        LEFT JOIN mls."member" la
            ON p.mls_definition_id = la.mls_definition_id
        AND p.list_agent_mls_id = la.mls_id
        LEFT JOIN mls."member" ba
            ON p.mls_definition_id = ba.mls_definition_id
        AND p.buyer_agent_mls_id = ba.mls_id
        WHERE p.close_date >= CURRENT_DATE - INTERVAL '12 months'
    ),
    Sides AS (
        SELECT
            la_license_number AS agent_license,
            'listing' AS side,
            list_price,
            close_price,
            property_type,
            close_date,
            address,
            la_name AS agent_name,
            la_email AS agent_email
        FROM BaseProperties
        WHERE la_license_number IN ({licenses_str})

        UNION ALL

        SELECT
            ba_license_number AS agent_license,
            'buyer' AS side,
            list_price,
            close_price,
            property_type,
            close_date,
            address,
            ba_name AS agent_name,
            ba_email AS agent_email
        FROM BaseProperties
        WHERE ba_license_number IN ({licenses_str})
    )
    SELECT *
    FROM Sides
    """
    
    return load_db_table(config_db, query)

def process_production(df: pd.DataFrame, roster: Dict[str, str]) -> Dict[str, Any]:
    """Calculates GCI, Top Producers, Revenue Shares, and MRR potential."""
    seat_count = len(roster)
    mrr = calculate_jointly_business_mrr(seat_count)

    if df.empty:
        return {
            "summary": {
                "total_sides": 0,
                "seat_count": seat_count,
                "mrr_potential": mrr,
                "sales_sides": 0,
                "lease_sides": 0,
                "sales_gci": 0.0,
                "leases_gci": 0.0,
                "total_gci": 0.0,
                "distribution": {
                    "sales": {"buyer": 0, "listing": 0},
                    "leases": {"tenant": 0, "listing": 0}
                }
            },
            "revenue_share": {
                "lease_application": 0.0,
                "concierge": 0.0,
                "total": 0.0
            },
            "top_producers": {
                "sales": [],
                "leases": []
            }
        }
    
    # Identify Sales vs Leases
    # Property types for leases often include 'Lease', 'RR', 'RL'
    lease_mask = df['property_type'].str.contains('Lease', case=False, na=False) | \
                 df['property_type'].isin(['RR', 'RL'])
    
    sales_df = df[~lease_mask]
    leases_df = df[lease_mask]
    
    # GCI Calculations
    sales_gci = (sales_df['close_price'] * 0.03).sum()
    leases_gci = (leases_df['close_price'] * 0.50).sum()
    
    # Side Distributions
    buyer_sides = len(sales_df[sales_df['side'] == 'buyer'])
    listing_sides = len(sales_df[sales_df['side'] == 'listing'])
    tenant_sides = len(leases_df[leases_df['side'] == 'buyer']) # 'buyer' in lease context is tenant
    lease_listing_sides = len(leases_df[leases_df['side'] == 'listing'])
    
    # Revenue Shares
    lease_app_share = lease_listing_sides * 28
    concierge_share = (buyer_sides + tenant_sides) * 0.30 * 42
    
    # Top Producers
    def get_top_5(data_df):
        agent_stats = data_df.groupby('agent_license').agg({
            'close_price': ['count', 'sum']
        })
        agent_stats.columns = ['units', 'volume']
        agent_stats = agent_stats.sort_values(by='units', ascending=False).head(5)
        
        top_list = []
        for lic, row in agent_stats.iterrows():
            name = roster.get(str(lic), f"Unknown ({lic})")
            top_list.append({
                "name": name,
                "license": lic,
                "units": int(row['units']),
                "volume": float(row['volume'])
            })
        return top_list

    return {
        "summary": {
            "total_sides": len(df),
            "seat_count": seat_count,
            "mrr_potential": mrr,
            "sales_sides": len(sales_df),
            "lease_sides": len(leases_df),
            "sales_gci": float(sales_gci),
            "leases_gci": float(leases_gci),
            "total_gci": float(sales_gci + leases_gci),
            "distribution": {
                "sales": {"buyer": buyer_sides, "listing": listing_sides},
                "leases": {"tenant": tenant_sides, "listing": lease_listing_sides}
            }
        },
        "revenue_share": {
            "lease_application": float(lease_app_share),
            "concierge": float(concierge_share),
            "total": float(lease_app_share + concierge_share)
        },
        "top_producers": {
            "sales": get_top_5(sales_df),
            "leases": get_top_5(leases_df)
        }
    }

def main():
    if len(sys.argv) < 2:
        print("Usage: python brokerage_deep_dive.py <broker_license>")
        sys.exit(1)
        
    broker_license = sys.argv[1]
    
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
        # Clean license (remove -B, -BB, etc.)
        clean_lic = lic.split("-")[0]
        roster[clean_lic] = name
    
    # Add Sponsored Agents to roster
    for agent_str in agents:
        if " (" in agent_str:
            name, lic = agent_str.rsplit(" (", 1)
            lic = lic.rstrip(")")
            # Clean license (remove -SA, etc.)
            clean_lic = lic.split("-")[0]
            roster[clean_lic] = name
            
    print(f"Found {len(roster)} agents (including Designated Broker).")
    
    if not roster:
        print("No agents found. Exiting.")
        return
        
    print("Step 3: Querying Production Database (Last 12 Months)...")
    licenses = list(roster.keys())
    # Handle massive rosters by batching queries if needed (though PG handles ~1000 IN items)
    df = get_production_data(licenses)
    print(f"Retrieved {len(df)} transaction sides.")
    
    print("Step 4: Processing Production Data...")
    analysis = process_production(df, roster)
    
    # Output result as JSON for potential piping, but also print summary
    print("\n" + "="*40)
    print("GROWTH PROFILE SUMMARY")
    print("="*40)
    s = analysis['summary']
    print(f"Roster Size: {s['seat_count']} analyzed seats")
    print(f"Total Sides: {s['total_sides']}")
    print(f"Sales: {s['sales_sides']} sides ({s['distribution']['sales']['buyer']} Buyer / {s['distribution']['sales']['listing']} Listing) | GCI: ${s['sales_gci']:,.2f}")
    print(f"Leases: {s['lease_sides']} sides ({s['distribution']['leases']['tenant']} Tenant / {s['distribution']['leases']['listing']} Listing) | GCI: ${s['leases_gci']:,.2f}")
    print(f"Total Estimated Brokerage GCI: ${s['total_gci']:,.2f}")

    print(f"\n--- Platform Revenue Potential ---")
    print(f"Estimated Monthly Subscription (MRR): ${s['mrr_potential']:,.2f}")

    print("\n--- Potential Revenue Share ---")
    rs = analysis['revenue_share']
    print(f"Lease Application Share: ${rs['lease_application']:,.2f}")
    print(f"Concierge Share: ${rs['concierge']:,.2f}")
    print(f"Total Share Opportunity: ${rs['total']:,.2f}")
    
    print("\n--- Top 5 Sales Producers ---")
    for i, p in enumerate(analysis['top_producers']['sales'], 1):
        print(f"{i}. {p['name']} ({p['license']}): {p['units']} units (${p['volume']:,.2f})")
        
    print("\n--- Top 5 Lease Producers ---")
    for i, p in enumerate(analysis['top_producers']['leases'], 1):
        print(f"{i}. {p['name']} ({p['license']}): {p['units']} units (${p['volume']:,.2f})")
    
    print("="*40)

if __name__ == "__main__":
    main()
