import sys
from pathlib import Path
import pandas as pd
import importlib.util
import json

# Add project root to sys.path
project_root = Path.cwd()
sys.path.insert(0, str(project_root))

# Import function from script with numeric name
spec = importlib.util.spec_from_file_location("brokerage_deep_dive", project_root / "04.dev" / "scripts" / "brokerage_deep_dive.py")
bdd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bdd)

get_production_data = bdd.get_production_data
process_production = bdd.process_production

roster = {
    "516829": "Andre Kocher",
    "516511": "Kelli Kocher",
    "671893": "Angela Roberts",
    "688885": "Patrick Kocher",
    "714189": "Tiffany Kocher",
    "768305": "Jon Wood",
    "655391": "Mandy Friday",
    "790827": "Lacha Carpenter",
    "609854": "Wendye Keasler",
    "367119": "Sheri Briscoe"
}

licenses = list(roster.keys())

print("Fetching production data for Kocher Team...")
df = get_production_data(licenses)

if not df.empty:
    analysis = process_production(df, roster)
    print(json.dumps(analysis, indent=2))
else:
    print("No production data found.")
