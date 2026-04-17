# Import libraries
from configparser import ConfigParser
import os

def get_project_root():
    """Returns the absolute path to the project root directory"""
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def get_config(config_file: str, section: str) -> dict:
    """
    Reads configuration from a file in the secrets directory.
    
    Args:
        config_file (str): Name of the config file (e.g. 'database.ini', 'airtable.ini')
        section (str): Section name in the config file (e.g. 'postgresql', 'airtable')
        
    Returns:
        dict: Configuration parameters
    """
    # Create a parser
    parser = ConfigParser()
    
    # Get the full path to the config file
    config_path = os.path.join(get_project_root(), 'secrets', config_file)
    
    # Check if file exists
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found at: {config_path}")
    
    # Read the configuration file
    parser.read(config_path)
    
    # Check if the section exists
    if not parser.has_section(section):
        raise Exception(f"Section {section} not found in {config_file}")
    
    # Convert config parameters to dictionary
    return dict(parser.items(section))

def get_db_config(config_file: str = 'database.ini') -> dict:
    """Convenience function for database config"""
    return get_config(config_file, 'postgresql')

def get_airtable_config(config_file: str = 'airtable.ini') -> dict:
    """Convenience function for Airtable config"""
    return get_config(config_file, 'airtable')

def get_api_config(config_file: str = 'api.ini') -> dict:
    """Convenience function for API config"""
    return get_config(config_file, 'api')