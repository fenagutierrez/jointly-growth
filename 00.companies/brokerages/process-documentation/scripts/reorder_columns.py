import pandas as pd

def reorder_texas_brokerage_csv(file_path):
    """Enforces the official column order for growth intelligence files."""
    df = pd.read_csv(file_path)
    
    desired_order = [
        "Company Name",
        "Headquarters",
        "Presence",
        "Type",
        "Main City",
        "Website URL",
        "Designated Broker Name",
        "Total Active Sales Agents (March 2026)",
        "DBAs",
        "License Number",
        "Status",
        "Original License Date",
        "License Expiration Date",
        "Designated Broker License",
        "Team Names"
    ]
    
    # Check for missing columns
    existing_columns = [col for col in desired_order if col in df.columns]
    
    # Reorder and save
    df_reordered = df[existing_columns]
    df_reordered.to_csv(file_path, index=False)
    print(f"Reordered columns for {file_path}")

if __name__ == "__main__":
    PATH = "00.companies/brokerages/output/summaries/top_100_active_brokerages_march_2026.csv"
    reorder_texas_brokerage_csv(PATH)
