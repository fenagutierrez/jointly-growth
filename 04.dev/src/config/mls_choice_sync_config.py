"""
Configuration management for MLS Choice synchronization operations.
"""

from dataclasses import dataclass
from typing import List, Dict, Any
from datetime import datetime
import logging
import os
import sys


@dataclass
class MLSChoiceSyncConfig:
    """Configuration class for MLS Choice synchronization operations."""
    
    # Database configuration
    jointly_config_db: str = 'tmp.ini'
    mls_config_db: str = 'janet.ini'
    
    # Airtable configuration
    airtable_table: str = "users"
    
    # Data validation configuration
    required_columns: List[str] = None
    max_null_percentage: float = 0.1
    
    # Synchronization configuration
    key_fields: List[str] = None
    
    # MLS-specific configuration
    mls_definition_id: str = '852'
    mls_member_types: List[str] = None
    
    # Logging configuration
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.key_fields is None:
            self.key_fields = ['user id']
        
        if self.required_columns is None:
            self.required_columns = ['user_id', 'jointly_agent_license', 'mls_definition_id']
        
        if self.mls_member_types is None:
            self.mls_member_types = ['MLS Only Salesperson', 'MLS Only Broker']
    
    def validate_config(self) -> bool:
        """Validate configuration parameters."""
        if not self.jointly_config_db:
            raise ValueError("jointly_config_db cannot be empty")
        
        if not self.mls_config_db:
            raise ValueError("mls_config_db cannot be empty")
        
        if not self.airtable_table:
            raise ValueError("airtable_table cannot be empty")
        
        if self.max_null_percentage < 0 or self.max_null_percentage > 1:
            raise ValueError("max_null_percentage must be between 0 and 1")
        
        return True
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'mls_choice_sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stderr),
                logging.FileHandler(log_file)
            ]
        )
        return logging.getLogger(__name__)
