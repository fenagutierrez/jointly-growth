"""
Google Sheets utility functions for data manipulation and synchronization.
"""

import os
import pandas as pd
import numpy as np
import gspread
from gspread_dataframe import get_as_dataframe, set_with_dataframe
from config.config import get_config, get_project_root


def get_google_sheets_client():
    """
    Authenticates and returns a Google Sheets client.
    
    Returns:
        gspread.client.Client: Authenticated Google Sheets client
    """
    # Get Google service account configuration
    google_config = get_config('api.ini', 'google')
    SERVICE_ACCOUNT_FILE = os.path.join(
        get_project_root(), 
        'secrets', 
        google_config['service_account_file']
    )
    
    # Authenticate with Google Sheets API
    return gspread.service_account(filename=SERVICE_ACCOUNT_FILE)


def validate_upsert_result(gc, spreadsheet_name, sheet_name, key_columns):
    """
    Validates the result of an upsert operation by checking for duplicates.
    
    Parameters:
        gc (gspread.client.Client): Authenticated gspread client
        spreadsheet_name (str): Name of the Google Spreadsheet
        sheet_name (str): Name of the worksheet to validate
        key_columns (list): List of column names used as keys
        
    Returns:
        dict: Validation results including duplicate count and sample duplicates
    """
    try:
        # Open the Google Spreadsheet and get data
        spreadsheet = gc.open(spreadsheet_name)
        sheet = spreadsheet.worksheet(sheet_name)
        data = get_as_dataframe(sheet)
        data = data.dropna(how='all')  # Remove empty rows
        
        if len(data) == 0:
            return {"status": "empty", "message": "Sheet is empty"}
        
        # Check for duplicates based on key columns
        duplicates = data.duplicated(subset=key_columns, keep=False)
        duplicate_count = duplicates.sum()
        
        result = {
            "status": "success",
            "total_rows": len(data),
            "duplicate_count": duplicate_count,
            "has_duplicates": duplicate_count > 0
        }
        
        if duplicate_count > 0:
            # Get sample duplicates for debugging
            duplicate_rows = data[duplicates].sort_values(key_columns)
            result["sample_duplicates"] = duplicate_rows[key_columns].head(10).to_dict('records')
            result["message"] = f"Found {duplicate_count} duplicate rows based on key columns {key_columns}"
        else:
            result["message"] = "No duplicates found - upsert successful"
            
        return result
        
    except Exception as e:
        return {"status": "error", "message": f"Error validating upsert: {str(e)}"}


def upsert_to_gsheet(gc, spreadsheet_name, sheet_name, new_data, key_columns, validate=True):
    """
    Upserts data into a Google Sheet based on key columns.
    
    Parameters:
        gc (gspread.client.Client): Authenticated gspread client
        spreadsheet_name (str): Name of the Google Spreadsheet
        sheet_name (str): Name of the worksheet to update
        new_data (pd.DataFrame): Data to upsert
        key_columns (list): List of column names used to identify existing rows for updates
        validate (bool): Whether to validate the result after upserting
    """
    # Initialize counters
    update_count = 0
    insert_count = len(new_data)
    
    # Open the Google Spreadsheet
    spreadsheet = gc.open(spreadsheet_name)
    sheet = spreadsheet.worksheet(sheet_name)
    
    # Get existing data
    try:
        existing_data = get_as_dataframe(sheet)
        original_columns = existing_data.columns.tolist()
        print(original_columns)
        existing_data = existing_data.dropna(how='all')  # Remove empty rows
    except Exception as e:
        print(f"Error getting existing data: {str(e)}")
        existing_data = pd.DataFrame()
        original_columns = None
        
    
    if len(existing_data) == 0:
        # If sheet has no data rows, but might have headers, maintain column order
        if original_columns:
            # Reorder new data to match existing column order
            existing_original_cols = [col for col in original_columns if col in new_data.columns]
            new_cols = [col for col in new_data.columns if col not in original_columns]
            final_columns = existing_original_cols + new_cols
            new_data = new_data[final_columns]
        set_with_dataframe(sheet, new_data)
    else:
        # Make copies to avoid modifying original dataframes
        existing_data = existing_data.copy()
        new_data = new_data.copy()
        
        # Function to clean and normalize key column values
        def clean_key_column(series):
            """Clean and normalize a key column for consistent matching"""
            # Convert to string and handle NaN/None values
            cleaned = series.astype(str)
            # Remove .0 suffix that might occur when reading integers as floats from GSheets
            cleaned = cleaned.replace(r'\.0$', '', regex=True)
            # Replace 'nan', 'None', '<NA>' with empty string for consistency
            cleaned = cleaned.replace(['nan', 'None', '<NA>'], '')
            # Strip whitespace
            cleaned = cleaned.str.strip()
            return cleaned
        
        # Clean and normalize key columns for both dataframes
        for col in key_columns:
            if col in existing_data.columns and col in new_data.columns:
                # Standardize datetime representation if possible
                # Only attempt on datetime-like or object columns to avoid errors with numeric types
                if (pd.api.types.is_datetime64_any_dtype(new_data[col]) or new_data[col].dtype == 'object') and \
                   (pd.api.types.is_datetime64_any_dtype(existing_data[col]) or existing_data[col].dtype == 'object'):
                    try:
                        # Coerce to datetime, format, and fill non-datetimes with original
                        new_dt = pd.to_datetime(new_data[col], errors='coerce')
                        new_data[col] = new_dt.dt.strftime('%Y-%m-%d %H:%M:%S').fillna(new_data[col])
                        
                        existing_dt = pd.to_datetime(existing_data[col], errors='coerce')
                        existing_data[col] = existing_dt.dt.strftime('%Y-%m-%d %H:%M:%S').fillna(existing_data[col])
                    except Exception:
                        # If something goes wrong, continue with string representation
                        pass
                
                # Convert to string and clean to handle mixed types
                existing_data[col] = clean_key_column(existing_data[col])
                new_data[col] = clean_key_column(new_data[col])
        
        # Check for duplicates in key columns in new data and remove them
        if new_data.duplicated(subset=key_columns).any():
            print(f"Found {new_data.duplicated(subset=key_columns).sum()} duplicate rows in new data based on key columns. Keeping last occurrence.")
            new_data = new_data.drop_duplicates(subset=key_columns, keep='last')
        
        # Create a composite key for efficient matching
        def create_composite_key(df, key_cols):
            """Create a composite key by joining key column values"""
            return df[key_cols].apply(lambda x: '|'.join(x.astype(str)), axis=1)
        
        existing_keys = create_composite_key(existing_data, key_columns)
        new_keys = create_composite_key(new_data, key_columns)
        
        # Find which rows need to be updated vs inserted
        update_mask = new_keys.isin(existing_keys)
        insert_mask = ~update_mask
        
        update_count = update_mask.sum()
        insert_count = insert_mask.sum()
        
        # Start with existing data
        result_data = existing_data.copy()
        
        # Update existing rows
        if update_mask.any():
            update_data = new_data[update_mask].copy()
            update_keys = create_composite_key(update_data, key_columns)
            
            # For each row to update, find matching existing row and update it
            for idx, update_key in update_keys.items():
                existing_idx = existing_keys[existing_keys == update_key].index[0]
                
                # Update all columns from new data (except key columns which should be the same)
                for col in new_data.columns:
                    new_value = new_data.loc[idx, col]
                    
                    if col in result_data.columns:
                        # Handle data type compatibility
                        existing_dtype = result_data[col].dtype
                        
                        # Convert value to match existing column dtype
                        if pd.isna(new_value):
                            # Handle NaN values appropriately for each dtype
                            if pd.api.types.is_numeric_dtype(existing_dtype):
                                converted_value = pd.NA if existing_dtype == 'Int64' else np.nan
                            else:
                                converted_value = None
                        else:
                            try:
                                # Try to convert to the existing column's dtype
                                if pd.api.types.is_integer_dtype(existing_dtype):
                                    # For integer columns, convert string numbers to int
                                    if str(new_value).strip() == '':
                                        converted_value = pd.NA if existing_dtype == 'Int64' else np.nan
                                    else:
                                        converted_value = int(float(str(new_value)))
                                elif pd.api.types.is_float_dtype(existing_dtype):
                                    # For float columns, convert empty strings to NaN
                                    if str(new_value).strip() == '':
                                        converted_value = np.nan
                                    else:
                                        converted_value = float(str(new_value))
                                elif pd.api.types.is_bool_dtype(existing_dtype):
                                    # For boolean columns
                                    if str(new_value).lower() in ['true', '1', 'yes']:
                                        converted_value = True
                                    elif str(new_value).lower() in ['false', '0', 'no', '']:
                                        converted_value = False
                                    else:
                                        converted_value = bool(new_value)
                                else:
                                    # For string/object columns, convert to string
                                    converted_value = str(new_value) if new_value is not None else None
                            except (ValueError, TypeError):
                                # If conversion fails, convert to string
                                converted_value = str(new_value) if new_value is not None else None
                        
                        result_data.loc[existing_idx, col] = converted_value
                    else:
                        # Add new column if it doesn't exist
                        result_data[col] = None
                        result_data.loc[existing_idx, col] = new_value
        
        # Insert new rows
        if insert_mask.any():
            insert_data = new_data[insert_mask].copy()
            
            # Ensure insert_data has all columns from result_data
            for col in result_data.columns:
                if col not in insert_data.columns:
                    insert_data[col] = None
            
            # Ensure result_data has all columns from insert_data
            for col in insert_data.columns:
                if col not in result_data.columns:
                    result_data[col] = None
            
            # Reorder insert_data columns to match result_data
            insert_data = insert_data[result_data.columns]
            
            # Concatenate new rows
            result_data = pd.concat([result_data, insert_data], ignore_index=True)
        
        # Reorder columns to match original if possible
        if original_columns:
            # Only include original columns that actually exist in result_data
            existing_original_cols = [col for col in original_columns if col in result_data.columns]
            # Get new columns that weren't in original
            new_cols = [col for col in result_data.columns if col not in original_columns]
            # Combine existing original columns with any new ones
            final_columns = existing_original_cols + new_cols
            # Reorder the DataFrame to maintain original column order
            result_data = result_data[final_columns]
            
        # Clear and write result data
        sheet.clear()
        set_with_dataframe(sheet, result_data)

    print(f"Upsert completed: {len(new_data)} rows processed ({update_count} updated, {insert_count} inserted).")

    if validate:
        return validate_upsert_result(gc, spreadsheet_name, sheet_name, key_columns)


def insert_to_gsheet(gc, spreadsheet_name, sheet_name, new_data):
    """
    Inserts data into a Google Sheet, clearing existing content.
    
    Parameters:
        gc (gspread.client.Client): Authenticated gspread client
        spreadsheet_name (str): Name of the Google Spreadsheet
        sheet_name (str): Name of the worksheet to update
        new_data (pd.DataFrame): Data to insert
    """
    # Open the Google Spreadsheet
    spreadsheet = gc.open(spreadsheet_name)
    sheet = spreadsheet.worksheet(sheet_name)
    
    # Write the updated data back to Google Sheets
    sheet.clear()  # Clears the sheet before writing
    set_with_dataframe(sheet, new_data)

    print(f"Insert completed: {len(new_data)} rows processed.")


def add_week_number_column(df, date_column, new_column_name='year_week_number'):
    """
    Adds a year-week-number column to a DataFrame based on a date column.
    Week numbers start with the week containing January 1st.
    
    Parameters:
        df (pd.DataFrame): Input DataFrame
        date_column (str): Name of the column containing dates
        new_column_name (str): Name of the new column to create
        
    Returns:
        pd.DataFrame: DataFrame with the new week number column
    """
    # Convert to datetime if not already
    if not pd.api.types.is_datetime64_any_dtype(df[date_column]):
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
    
    # Add year-week-number column using %V for ISO week numbers
    # ISO week 1 is the week containing January 1st
    df[new_column_name] = df[date_column].dt.strftime('%G-%V')
    
    return df