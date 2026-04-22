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
    # Target Lists for Kelly Simon Properties
    target_lics = [
        "572128", # Kelly Simon
        "772108", # Veronica Miller
        "637294", # Jennifer Vickers
        "671546", # Erin Dominy
        "650360", # Lauren Neely
        "823549", # Trace Brown
        "670411", # Shelly Thomas
        "522332", # Larissa McGinnis
        "779326"  # Lindsey Jahns
    ]

    target_names = [
        "Kelly Simon",
        "Veronica Miller",
        "Jennifer Vickers",
        "Erin Dominy",
        "Lauren Neely",
        "Trace Brown",
        "Shelly Thomas",
        "Larissa McGinnis",
        "Lindsey Jahns",
        "Carrie Teague",
        "Amy Klein",
        "Denise Thompson",
        "Julie Harrison"
    ]
    
    print("Fetching contact information...")
    df = get_agent_contacts(target_lics, target_names)
    
    if not df.empty:
        # Deduplicate by name and license
        df = df.drop_duplicates(subset=['name', 'email'])
        print(df.to_string(index=False))
    else:
        print("No contacts found.")
