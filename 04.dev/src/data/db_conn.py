# Import libraries
import pandas as pd
import psycopg2
from config.config import get_db_config

def load_db_table(config_db: str, query: str) -> pd.DataFrame:
    """
    Loads data from database using the provided query.
    
    Args:
        config_db (str): Name of the config file
        query (str): SQL query to execute
        
    Returns:
        pd.DataFrame: Query results as a pandas DataFrame
    """
    try:
        # Get database parameters
        params = get_db_config(config_db)
        
        # Connect to database
        engine = psycopg2.connect(**params)
        
        try:
            # Execute query and return results
            data = pd.read_sql(query, con=engine)
            if 'id' not in data.columns:
                data['id'] = None
            return data
        finally:
            engine.close()
            
    except Exception as e:
        raise Exception(f"Database error: {str(e)}")