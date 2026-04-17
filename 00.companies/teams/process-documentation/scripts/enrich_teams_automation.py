import pandas as pd
import numpy as np
import os

def calculate_mrr(agents):
    """Calculates MRR based on the Jointly Business pricing structure."""
    if not agents or agents == 'Unknown':
        return 0.0
    
    try:
        agents = int(float(str(agents).replace(',', '')))
    except ValueError:
        return 0.0

    base_fee = 249.0
    if agents <= 5:
        return base_fee
    
    mrr = base_fee
    
    # Tier 2: 6 to 25 ($25/seat)
    tier2_seats = min(agents - 5, 20)
    mrr += tier2_seats * 25.0
    
    if agents <= 25:
        return mrr
    
    # Tier 3: 26 to 49 ($15/seat)
    tier3_seats = min(agents - 25, 24)
    mrr += tier3_seats * 15.0
    
    if agents <= 49:
        return mrr
    
    # Tier 4: 50 to 99 ($10/seat)
    tier4_seats = min(agents - 49, 50)
    mrr += tier4_seats * 10.0
    
    if agents <= 99:
        return mrr
    
    # Tier 5: 100+ ($5/seat)
    tier5_seats = agents - 99
    mrr += tier5_seats * 5.0
    
    return mrr

def map_metro_area(location):
    """Maps a city/location to a broader Texas Metro Area."""
    if not location or pd.isna(location):
        return "Other TX"
    
    loc = str(location).lower()
    
    houston_cities = ['houston', 'katy', 'cypress', 'the woodlands', 'tomball', 'sugar land', 'pearland', 'league city', 'spring', 'kingwood', 'brenham', 'bellaire', 'baytown', 'dickinson', 'falshear', 'fulshear', 'willis']
    dfw_cities = ['dallas', 'fort worth', 'plano', 'frisco', 'arlington', 'mckinney', 'flower mound', 'denton', 'colleyville', 'southlake', 'richardson', 'waxahachie', 'allen', 'grapevine', 'the colony', 'rockwall', 'mansfield', 'wylie', 'irving', 'prosper', 'weatherford', 'argyle', 'pantego', 'midlothian', 'the colony', 'harker heights']
    austin_cities = ['austin', 'round rock', 'georgetown', 'cedar park', 'dripping springs', 'lockhart', 'lakeway', 'lake travis', 'west lake hills', 'mcqueeney', 'hudson oaks']
    sa_cities = ['san antonio', 'new braunfels', 'boerne', 'fredericksburg', 'del rio']
    el_paso_cities = ['el paso']
    rgv_cities = ['mcallen', 'brownsville', 'laredo', 'south padre island', 'corpus christi', 'victoria']
    
    if any(city in loc for city in houston_cities):
        return "Houston"
    if any(city in loc for city in dfw_cities):
        return "DFW"
    if any(city in loc for city in austin_cities):
        return "Austin"
    if any(city in loc for city in sa_cities):
        return "San Antonio"
    if any(city in loc for city in el_paso_cities):
        return "El Paso"
    if any(city in loc for city in rgv_cities):
        return "RGV"
    
    return "Other TX"

def enrich_csv(file_path):
    df = pd.read_csv(file_path)
    
    # Add new columns if they don't exist
    new_cols = ['teamLeadName', 'teamLeadEmail', 'teamLeadPhone', 'mrr', 'metroArea']
    for col in new_cols:
        if col not in df.columns:
            df[col] = ""
            
    # Automated Enrichments
    df['mrr'] = df['agents'].apply(calculate_mrr)
    df['metroArea'] = df['location'].apply(map_metro_area)
    
    # Format MRR as currency
    df['mrr'] = df['mrr'].apply(lambda x: f"${x:,.2f}")
    
    # Reorder columns
    cols = list(df.columns)
    ordered_cols = ['teamName', 'teamLeadName', 'teamLeadEmail', 'teamLeadPhone', 'mrr', 'metroArea']
    
    final_cols = ordered_cols + [c for c in cols if c not in ordered_cols]
    df = df[final_cols]
    
    df.to_csv(file_path, index=False)
    print(f"Successfully enriched {file_path}")

if __name__ == "__main__":
    TARGETS = [
        "00.companies/teams/output/summaries/all_medium_teams_texas.csv",
        "00.companies/teams/output/summaries/all_large_teams_texas.csv"
    ]
    for target in TARGETS:
        if os.path.exists(target):
            enrich_csv(target)
        else:
            print(f"File not found: {target}")
