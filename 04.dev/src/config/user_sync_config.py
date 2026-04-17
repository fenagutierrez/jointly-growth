"""
Configuration management for user synchronization operations.
"""


from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import logging
import os
import sys


@dataclass
class UserSyncConfig:
    """Configuration class for user synchronization operations."""
    
    # Database configuration
    config_db: str = 'tmp.ini'
    
    # Data processing configuration
    months_2025: List[str] = None
    subset_columns: List[str] = None
    key_fields: List[str] = None
    
    # Airtable configuration
    airtable_table: str = "users"
    
    # Google Sheets configuration
    gsheet_name: str = "new users"
    gsheet_worksheet: str = "new_users_db"
    gsheet_key_columns: List[str] = None
    
    # Data validation configuration
    required_columns: List[str] = None
    max_null_percentage: float = 0.1
    
    # Logging configuration
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.months_2025 is None:
            self.months_2025 = [
                '2025-01-01', '2025-02-01', '2025-03-01', '2025-04-01', 
                '2025-05-01', '2025-06-01', '2025-07-01', '2025-08-01', 
                '2025-09-01', '2025-10-01', '2025-11-01', '2025-12-01'
            ]
        
        if self.subset_columns is None:
            self.subset_columns = [
                'for_sale_count', 'for_sale_count_last_7_days', 
                'for_sale_count_last_30_days', 'for_rent_count', 
                'for_rent_count_last_7_days', 'for_rent_count_last_30_days'
            ]
        
        if self.key_fields is None:
            self.key_fields = ['user id']
        
        if self.gsheet_key_columns is None:
            self.gsheet_key_columns = ['id']
        
        if self.required_columns is None:
            self.required_columns = ['id', 'email', 'status']
    
    def get_month_columns(self) -> List[str]:
        """Get formatted month column names for login tracking."""
        return [f'logged_in_{pd.to_datetime(month).strftime("%Y_%m")}' 
                for month in self.months_2025]
    
    def validate_config(self) -> bool:
        """Validate configuration parameters."""
        if not self.config_db:
            raise ValueError("config_db cannot be empty")
        
        if not self.airtable_table:
            raise ValueError("airtable_table cannot be empty")
        
        if not self.gsheet_name or not self.gsheet_worksheet:
            raise ValueError("Google Sheets configuration incomplete")
        
        if self.max_null_percentage < 0 or self.max_null_percentage > 1:
            raise ValueError("max_null_percentage must be between 0 and 1")
        
        return True
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'user_sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stderr),
                logging.FileHandler(log_file)
            ]
        )
        return logging.getLogger(__name__)


# Import pandas here to avoid circular imports
import pandas as pd
