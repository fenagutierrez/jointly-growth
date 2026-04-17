import pandas as pd

def batch_update(file_path, logic_dict, target_col):
    """
    Updates a target column based on keywords in the 'Company Name'.
    Example logic_dict: {"KELLER WILLIAMS": "Franchise", "COMPASS": "Independent"}
    """
    df = pd.read_csv(file_path)
    
    for keyword, value in logic_dict.items():
        mask_name = df['Company Name'].str.contains(keyword, case=False, na=False)
        mask_dba = df['DBAs'].str.contains(keyword, case=False, na=False)
        mask = mask_name | mask_dba
        df.loc[mask, target_col] = value
        print(f"Updated {mask.sum()} rows for keyword '{keyword}' with '{value}'")
    
    df.to_csv(file_path, index=False)

if __name__ == "__main__":
    PATH = "00.companies/brokerages/output/summaries/top_100_active_brokerages_march_2026.csv"

    # Example logic for Type
    type_logic = {
        "KELLER WILLIAMS": "Franchise",
        "COLDWELL BANKER": "Franchise",
        "RE/MAX": "Franchise",
        "CENTURY 21": "Franchise"
    }
    # batch_update(PATH, type_logic, "Type")
