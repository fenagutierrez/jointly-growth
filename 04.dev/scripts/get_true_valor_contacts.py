#!/usr/bin/env python3
import sys
import pandas as pd
from pathlib import Path

# Add project root to sys.path
current_dir = Path(__file__).parent.absolute()
project_root = current_dir.parent.absolute()
sys.path.insert(0, str(project_root))

from scripts.get_agent_contacts import get_agent_contacts

if __name__ == "__main__":
    # True Valor Realty Targets
    target_lics = [
        "669239", # NOAH BALLARD (Broker)
        "726333", # MONICA ARACELI GARCIA (Top Sales & Lease)
        "814431", # TAMI JOYCE BAILEY
        "809044", # VIVIANA TEJADA-CAVAZOS
        "749268", # CARLITTA NJIE
        "815179", # ASHLYN FRANCES REYNA
        "818252", # VERONICA A LEYVA
        "814880", # BRENNA JAMES
        "802189", # GABRIELLA MARIE GUAJARDO
        "838383"  # KYLE MERRILL
    ]

    target_names = [
        "NOAH BALLARD",
        "MONICA GARCIA",
        "TAMI BAILEY",
        "VIVIANA TEJADA",
        "CARLITTA NJIE",
        "ASHLYN REYNA",
        "VERONICA LEYVA",
        "BRENNA JAMES",
        "GABRIELLA GUAJARDO",
        "KYLE MERRILL"
    ]
    
    print("Fetching contact information for True Valor Realty...")
    df = get_agent_contacts(target_lics, target_names)
    
    if not df.empty:
        # Deduplicate by name and license
        df = df.drop_duplicates(subset=['name', 'email'])
        print(df.to_string(index=False))
    else:
        print("No contacts found.")
