"""
Configuration management for team synchronization operations.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import logging
import os
import sys


@dataclass
class TeamSyncConfig:
    """Configuration class for team synchronization operations."""
    
    # Database configuration
    config_db: str = 'tmp.ini'
    
    # Airtable configuration
    airtable_table: str = "teams"
    
    # Google Sheets configuration (if needed in the future)
    gsheet_name: str = "teams_data"
    gsheet_worksheet: str = "teams_db"
    gsheet_key_columns: List[str] = None
    
    # Data validation configuration
    required_columns: List[str] = None
    max_null_percentage: float = 0.1
    
    # Synchronization configuration
    key_fields: List[str] = None
    
    # Logging configuration
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.key_fields is None:
            self.key_fields = ['team id']
        
        if self.gsheet_key_columns is None:
            self.gsheet_key_columns = ['id']
        
        if self.required_columns is None:
            self.required_columns = ['id', 'name', 'status']
    
    def validate_config(self) -> bool:
        """Validate configuration parameters."""
        if not self.config_db:
            raise ValueError("config_db cannot be empty")
        
        if not self.airtable_table:
            raise ValueError("airtable_table cannot be empty")
        
        if self.max_null_percentage < 0 or self.max_null_percentage > 1:
            raise ValueError("max_null_percentage must be between 0 and 1")
        
        return True
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'team_sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stderr),
                logging.FileHandler(log_file)
            ]
        )
        return logging.getLogger(__name__)

