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
from src.utils.pricing import calculate_jointly_business_mrr

def get_production_data(agent_licenses: List[str], config_db: str = "janet.ini") -> pd.DataFrame:
    """Queries production data for the last 12 months for a list of licenses."""
    if not agent_licenses:
        return pd.DataFrame()
    
    # Clean licenses
    cleaned = []
    for lic in agent_licenses:
        c = ''.join(filter(str.isdigit, str(lic))).lstrip('0')
        if c:
            cleaned.append(f"'{c}'")
            
    if not cleaned:
        return pd.DataFrame()
            
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
    if not roster:
        return {}
    
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
            "revenue_share": {"lease_application": 0.0, "concierge": 0.0, "total": 0.0},
            "top_producers": {"sales": [], "leases": []}
        }
    
    # Identify Sales vs Leases
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
    tenant_sides = len(leases_df[leases_df['side'] == 'buyer']) 
    lease_listing_sides = len(leases_df[leases_df['side'] == 'listing'])
    
    # Revenue Shares
    lease_app_share = lease_listing_sides * 28
    concierge_share = (buyer_sides + tenant_sides) * 0.30 * 42
    
    # Top Producers
    def get_top_5(data_df):
        if data_df.empty:
            return []
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
    parser = argparse.ArgumentParser(description="Analyze team production based on agent licenses.")
    parser.add_argument("--licenses", type=str, help="Comma-separated list of agent licenses.")
    parser.add_argument("--roster_file", type=str, help="Path to a JSON file containing {license: name} mapping.")
    parser.add_argument("--config", type=str, default="janet.ini", help="Database config file.")
    
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

    print(f"--- Analyzing Team Production for {len(roster)} Seats ---")
    
    licenses = list(roster.keys())
    df = get_production_data(licenses, args.config)
    print(f"Retrieved {len(df)} transaction sides for the last 12 months.")
    
    analysis = process_production(df, roster)
    if not analysis:
        print("No production data found for these licenses.")
        return

    print("\n" + "="*40)
    print("TEAM GROWTH PROFILE SUMMARY")
    print("="*40)
    s = analysis['summary']
    print(f"Roster Size: {s['seat_count']} analyzed seats")
    print(f"Total Sides: {s['total_sides']}")
    print(f"Sales: {s['sales_sides']} sides ({s['distribution']['sales']['buyer']} Buyer / {s['distribution']['sales']['listing']} Listing) | GCI: ${s['sales_gci']:,.2f}")
    print(f"Leases: {s['lease_sides']} sides ({s['distribution']['leases']['tenant']} Tenant / {s['distribution']['leases']['listing']} Listing) | GCI: ${s['leases_gci']:,.2f}")
    print(f"Total Estimated Team GCI: ${s['total_gci']:,.2f}")
    
    print(f"\n--- Platform Revenue Potential ---")
    print(f"Estimated Monthly Subscription (MRR): ${s['mrr_potential']:,.2f}")
    
    print("\n--- Potential Jointly Revenue Share ---")
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
