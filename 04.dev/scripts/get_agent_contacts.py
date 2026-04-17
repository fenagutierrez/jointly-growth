#!/usr/bin/env python3
import sys
import pandas as pd
from pathlib import Path

# Add project root to sys.path
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.absolute()
sys.path.insert(0, str(project_root))

from src.data.db_conn import load_db_table

def get_agent_contacts(licenses=None, names=None, config_db="janet.ini"):
    conditions = []
    
    if licenses:
        cleaned_lics = []
        for lic in licenses:
            c = ''.join(filter(str.isdigit, str(lic))).lstrip('0')
            if c:
                cleaned_lics.append(f"'{c}'")
        if cleaned_lics:
            # Check both mls_id and state_license
            lic_str = ", ".join(cleaned_lics)
            conditions.append(f"(NULLIF(LTRIM(REGEXP_REPLACE(state_license, '[^0-9]', '', 'g'), '0'), '') IN ({lic_str}) OR NULLIF(LTRIM(REGEXP_REPLACE(mls_id, '[^0-9]', '', 'g'), '0'), '') IN ({lic_str}))")
            
    if names:
        name_conds = []
        for name in names:
            name_conds.append(f"listing_agent_name ILIKE '%{name}%'")
        if name_conds:
            conditions.append("(" + " OR ".join(name_conds) + ")")
            
    if not conditions:
        return pd.DataFrame()
        
    where_clause = " OR ".join(conditions)
    
    query = f"""
    SELECT 
        listing_agent_name as name,
        state_license as license,
        listing_agent_email as email,
        listing_agent_phone as phone,
        status,
        brokerage_name
    FROM mls.member
    WHERE {where_clause}
    ORDER BY updated_on DESC
    """
    
    return load_db_table(config_db, query)

if __name__ == "__main__":
    # Target Lists for M. Stagers & Partners Realty LLC
    target_lics = [
        "435856", # MELISSA STAGERS (Broker/Owner)
        "515473", # ARA LONG FESPERMAN (Broker Associate)
        "741134", # DANA C. DANNELLY (Top Sales)
        "561284", # KERRY R DIKE (Top Sales)
        "759130", # ANIZA OZELLE LOPEZ (Top Sales/Lease)
        "630958", # SARA ELIZABETH RYAN (Top Sales)
        "681079", # KIMBERLY REED (Top Sales)
        "729796", # SETH BURNS (Top Lease)
        "584316", # JESSICA STAGERS (Management)
        "727094"  # RACHEL ALMANZAR (Top Producer/Management)
    ]

    target_names = [
        "MELISSA STAGERS",
        "MISSY STAGERS",
        "ARA FESPERMAN",
        "ADDIE LANGEHENNIG",
        "COURTNEY MORENO",
        "JESSICA PINON",
        "JESSICA STAGERS",
        "DANNY MARTINEZ",
        "DANA DANNELLY",
        "KERRY DIKE",
        "ANIZA LOPEZ",
        "SARA RYAN",
        "LIBBY RYAN",
        "KIMBERLY REED",
        "SETH BURNS",
        "RACHEL ALMANZAR"
    ]
    
    print("Fetching contact information...")
    df = get_agent_contacts(target_lics, target_names)
    
    if not df.empty:
        # Deduplicate by name and license
        df = df.drop_duplicates(subset=['name', 'email'])
        print(df.to_string(index=False))
    else:
        print("No contacts found.")
