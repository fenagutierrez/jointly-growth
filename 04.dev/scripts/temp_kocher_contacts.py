import sys
from pathlib import Path
import pandas as pd
import psycopg2
from configparser import ConfigParser

# Add project root to sys.path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

def load_db_table(config_file, query):
    # Simplified load_db_table for this purpose
    config_path = project_root / "04.dev" / "secrets" / config_file
    parser = ConfigParser()
    parser.read(config_path)
    
    db_config = {}
    if parser.has_section('postgresql'):
        params = parser.items('postgresql')
        for param in params:
            db_config[param[0]] = param[1]
    
    conn = psycopg2.connect(**db_config)
    df = pd.read_sql(query, conn)
    conn.close()
    return df

def get_agent_contacts(names=None):
    if not names:
        return pd.DataFrame()
    
    name_conds = []
    for name in names:
        name_conds.append(f"listing_agent_name ILIKE '%{name}%'")
    where_clause = " OR ".join(name_conds)
    
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
    
    return load_db_table("janet.ini", query)

names = ["Andre Kocher", "Kelli Kocher", "Angela Roberts", "Patrick Kocher", "Tiffany Kocher", "Amy Carpenter", "Jon Wood", "Mandy Friday", "Wendye Keasler", "Nancy Brown", "Sheri Briscoe", "Lacha Carpenter", "Lisa Vesterman"]

print("Fetching contacts for Kocher Team...")
df = get_agent_contacts(names=names)
if not df.empty:
    df = df.drop_duplicates(subset=['name', 'email'])
    print(df.to_string(index=False))
else:
    print("No contacts found.")
