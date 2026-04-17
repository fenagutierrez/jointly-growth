#!/usr/bin/env python3
import os
import sys
import pandas as pd
from pathlib import Path

# Add project root and script directory to sys.path
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.absolute()
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

from brokerage_deep_dive import get_agent_roster, get_production_data, process_production

def enrich_csv(input_csv, master_trec_csv, output_csv):
    print(f"Loading top 100 list: {input_csv}")
    df_top = pd.read_csv(input_csv)
    
    # Define new columns
    new_cols = [
        "Sale Buyers Sides", "Sale Listings Sides", 
        "Lease Tenants Sides", "Lease Listings Sides", 
        "Sale GCI", "Lease GCI", "Revenue Opportunity"
    ]
    
    # Initialize new columns if they don't exist
    for col in new_cols:
        if col not in df_top.columns:
            df_top[col] = 0.0
            
    # Find the index of "Total Active Sales Agents (March 2026)"
    target_idx = df_top.columns.get_loc("Total Active Sales Agents (March 2026)") + 1
    
    # Reorder columns to place new ones after Total Active Sales Agents
    cols = list(df_top.columns)
    # Remove new_cols from where they might be and insert them at target_idx
    for col in new_cols:
        cols.remove(col)
    
    for i, col in enumerate(new_cols):
        cols.insert(target_idx + i, col)
        
    df_top = df_top[cols]

    print(f"Starting enrichment for {len(df_top)} brokerages...")
    
    for index, row in df_top.iterrows():
        license_num = str(row["License Number"])
        company_name = row["Company Name"]
        
        print(f"[{index+1}/100] Processing: {company_name} ({license_num})")
        
        try:
            roster = get_agent_roster(license_num, master_trec_csv)
            if not roster:
                print(f"  - No roster found.")
                continue
                
            prod_df = get_production_data(list(roster.keys()))
            if prod_df.empty:
                print(f"  - No production data found.")
                continue
                
            analysis = process_production(prod_df, roster)
            
            s = analysis['summary']
            rs = analysis['revenue_share']
            
            df_top.at[index, "Sale Buyers Sides"] = s['distribution']['sales']['buyer']
            df_top.at[index, "Sale Listings Sides"] = s['distribution']['sales']['listing']
            df_top.at[index, "Lease Tenants Sides"] = s['distribution']['leases']['tenant']
            df_top.at[index, "Lease Listings Sides"] = s['distribution']['leases']['listing']
            df_top.at[index, "Sale GCI"] = round(s['sales_gci'], 2)
            df_top.at[index, "Lease GCI"] = round(s['leases_gci'], 2)
            df_top.at[index, "Revenue Opportunity"] = round(rs['total'], 2)
            
            print(f"  - Updated: {s['total_sides']} sides, ${rs['total']:,.2f} opportunity")
            
        except Exception as e:
            print(f"  - Error processing {company_name}: {e}")

    print(f"Saving enriched data to {output_csv}")
    df_top.to_csv(output_csv, index=False)
    print("Enrichment complete.")

if __name__ == "__main__":
    TOP_100_CSV = "00.companies/brokerages/output/summaries/top_100_active_brokerages_march_2026.csv"
    MASTER_TREC = "00.companies/brokerages/source/trec/Broker_and_Sales_Agent_License_Holder_Information_20260305.csv"
    
    enrich_csv(TOP_100_CSV, MASTER_TREC, TOP_100_CSV)
