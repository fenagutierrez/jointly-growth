import pandas as pd
import sys
import os

# Adjust path to reach the consolidated CSV relative to script location or use absolute path
# For consistency with other scripts in this folder, we assume execution from brokerage root or provided path
CSV_PATH = '00.companies/brokerages/output/summaries/top_1000_active_brokerages_consolidated.csv'

METRO_MAPPING = {
    'Abilene': 'Other Texas',
    'Addison': 'Dallas-Fort Worth (DFW)',
    'Albuquerque': 'Out of State',
    'Allen': 'Dallas-Fort Worth (DFW)',
    'Amarillo': 'Lubbock / Amarillo',
    'Argyle': 'Dallas-Fort Worth (DFW)',
    'Arlington': 'Dallas-Fort Worth (DFW)',
    'Austin': 'Austin',
    'Azle': 'Dallas-Fort Worth (DFW)',
    'Baytown': 'Houston',
    'Beaumont': 'Beaumont',
    'Bedford': 'Dallas-Fort Worth (DFW)',
    'Bellaire': 'Houston',
    'Belton': 'Waco / Temple / Killeen',
    'Birmingham': 'Out of State',
    'Boerne': 'San Antonio',
    'Brenham': 'Houston',
    'Brownsville': 'McAllen / RGV',
    'Bryan': 'Waco / Temple / Killeen',
    'Buda': 'Austin',
    'Burleson': 'Dallas-Fort Worth (DFW)',
    'Burlington': 'Out of State',
    'Canton': 'Dallas-Fort Worth (DFW)',
    'Canyon': 'Lubbock / Amarillo',
    'Carthage': 'Other Texas',
    'Cedar Park': 'Austin',
    'Celina': 'Dallas-Fort Worth (DFW)',
    'Chicago': 'Out of State',
    'Cibolo': 'San Antonio',
    'Clearwater': 'Out of State',
    'Clifton': 'Other Texas',
    'College Station': 'Waco / Temple / Killeen',
    'Collegeville': 'Out of State',
    'Conroe': 'Houston',
    'Coppell': 'Dallas-Fort Worth (DFW)',
    'Copperas Cove': 'Waco / Temple / Killeen',
    'Corpus Christi': 'Corpus Christi',
    'Corsicana': 'Other Texas',
    'Cypress': 'Houston',
    'Dallas': 'Dallas-Fort Worth (DFW)',
    'Decatur': 'Dallas-Fort Worth (DFW)',
    'Deer Park': 'Houston',
    'Denton': 'Dallas-Fort Worth (DFW)',
    'Denver': 'Out of State',
    'Dickinson': 'Houston',
    'Edinburg': 'McAllen / RGV',
    'El Paso': 'El Paso',
    'Fair Oaks Ranch': 'San Antonio',
    'Flower Mound': 'Dallas-Fort Worth (DFW)',
    'Forney': 'Dallas-Fort Worth (DFW)',
    'Fort Worth': 'Dallas-Fort Worth (DFW)',
    'Friendswood': 'Houston',
    'Frisco': 'Dallas-Fort Worth (DFW)',
    'Fulshear': 'Houston',
    'Galveston': 'Houston',
    'Garden Ridge': 'San Antonio',
    'Garland': 'Dallas-Fort Worth (DFW)',
    'Georgetown': 'Austin',
    'Granbury': 'Dallas-Fort Worth (DFW)',
    'Grand Prairie': 'Dallas-Fort Worth (DFW)',
    'Grapeland': 'Other Texas',
    'Grapevine': 'Dallas-Fort Worth (DFW)',
    'Greenville': 'Dallas-Fort Worth (DFW)',
    'Gun Barrel City': 'Dallas-Fort Worth (DFW)',
    'Harker Heights': 'Waco / Temple / Killeen',
    'Harlingen': 'McAllen / RGV',
    'Highland Village': 'Dallas-Fort Worth (DFW)',
    'Hoboken': 'Out of State',
    'Horseshoe Bay': 'Austin',
    'Houston': 'Houston',
    'Humble': 'Houston',
    'Huntsville': 'Houston',
    'Irving': 'Dallas-Fort Worth (DFW)',
    'Jacksonville': 'Tyler / Longview',
    'Katy': 'Houston',
    'Kerrville': 'Other Texas',
    'Kilgore': 'Tyler / Longview',
    'Killeen': 'Waco / Temple / Killeen',
    'Kingwood': 'Houston',
    'Lake Jackson': 'Houston',
    'Lake Mary': 'Out of State',
    'Lakeway': 'Austin',
    'Laredo': 'McAllen / RGV',
    'League City': 'Houston',
    'Leander': 'Austin',
    'Lewisville': 'Dallas-Fort Worth (DFW)',
    'Lindale': 'Tyler / Longview',
    'Little Elm': 'Dallas-Fort Worth (DFW)',
    'Longview': 'Tyler / Longview',
    'Lubbock': 'Lubbock / Amarillo',
    'Lufkin': 'Other Texas',
    'Mabank': 'Dallas-Fort Worth (DFW)',
    'Mansfield': 'Dallas-Fort Worth (DFW)',
    'McAllen': 'McAllen / RGV',
    'McKinney': 'Dallas-Fort Worth (DFW)',
    'Mesquite': 'Dallas-Fort Worth (DFW)',
    'Miami': 'Out of State',
    'Midland': 'Midland / Odessa',
    'Midlothian': 'Dallas-Fort Worth (DFW)',
    'Mission': 'McAllen / RGV',
    'Missouri City': 'Houston',
    'Montgomery': 'Houston',
    'Mount Pleasant': 'Other Texas',
    'New Braunfels': 'San Antonio',
    'New Caney': 'Houston',
    'New Waverly': 'Houston',
    'North Richland Hills': 'Dallas-Fort Worth (DFW)',
    'Odessa': 'Midland / Odessa',
    'Out of State': 'Out of State',
    'Palmer': 'Dallas-Fort Worth (DFW)',
    'Paris': 'Other Texas',
    'Pearland': 'Houston',
    'Pipe Creek': 'San Antonio',
    'Plano': 'Dallas-Fort Worth (DFW)',
    'Pleasanton': 'San Antonio',
    'Port Neches': 'Beaumont',
    'Porter': 'Houston',
    'Prosper': 'Dallas-Fort Worth (DFW)',
    'Richardson': 'Dallas-Fort Worth (DFW)',
    'Richmond': 'Houston',
    'Roanoke': 'Dallas-Fort Worth (DFW)',
    'Rochelle': 'Other Texas',
    'Rockport': 'Corpus Christi',
    'Rockwall': 'Dallas-Fort Worth (DFW)',
    'Round Rock': 'Austin',
    'Round Top': 'Austin',
    'Rowlett': 'Dallas-Fort Worth (DFW)',
    'San Angelo': 'Other Texas',
    'San Antonio': 'San Antonio',
    'San Marcos': 'Austin',
    'Schertz': 'San Antonio',
    'Scottsdale': 'Out of State',
    'Shavanno Park': 'San Antonio',
    'Sherman': 'Dallas-Fort Worth (DFW)',
    'Silverton': 'Other Texas',
    'Silsbee': 'Beaumont',
    'Southlake': 'Dallas-Fort Worth (DFW)',
    'Spring': 'Houston',
    'Stafford': 'Houston',
    'Stamford': 'Other Texas',
    'Strategic': 'Other Texas',
    'Sugar Land': 'Houston',
    'Taylor': 'Austin',
    'The Colony': 'Dallas-Fort Worth (DFW)',
    'The Woodlands': 'Houston',
    'Tomball': 'Houston',
    'Trophy Club': 'Dallas-Fort Worth (DFW)',
    'Tyler': 'Tyler / Longview',
    'Various (TX)': 'Other Texas',
    'Victoria': 'Other Texas',
    'Waco': 'Waco / Temple / Killeen',
    'Waxahachie': 'Dallas-Fort Worth (DFW)',
    'Weatherford': 'Dallas-Fort Worth (DFW)',
    'Webster': 'Houston',
    'West Palm Beach': 'Out of State',
    'Westlake': 'Dallas-Fort Worth (DFW)',
    'Whitesboro': 'Dallas-Fort Worth (DFW)',
    'Wichita Falls': 'Other Texas'
}

def apply_mapping(csv_path):
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    df = pd.read_csv(csv_path)
    
    # Add Metro Area column based on Main City
    df['Metro Area'] = df['Main City'].map(METRO_MAPPING)
    
    # Identifying missing mappings
    missing_cities = df[df['Metro Area'].isna()]['Main City'].unique()
    if len(missing_cities) > 0:
        print(f"Warning: No mapping found for cities: {missing_cities}. Defaulting to 'Other'.")
        df['Metro Area'] = df['Metro Area'].fillna('Other')
    
    # Ensure proper column ordering (Metro Area after Main City)
    cols = df.columns.tolist()
    if 'Metro Area' in cols and 'Main City' in cols:
        cols.pop(cols.index('Metro Area'))
        main_city_idx = cols.index('Main City')
        cols.insert(main_city_idx + 1, 'Metro Area')
        df = df[cols]
    
    df.to_csv(csv_path, index=False)
    print(f"Updated {csv_path} with Metro Area classifications.")

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else CSV_PATH
    apply_mapping(target)
