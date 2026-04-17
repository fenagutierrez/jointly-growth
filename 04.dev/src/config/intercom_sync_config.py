"""
Configuration management for Intercom synchronization operations.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import os
import sys


@dataclass
class IntercomSyncConfig:
    """Configuration class for Intercom synchronization operations."""
    
    # Date range configuration
    start_date: str = '2025-12-10'
    end_date: str = '2025-12-11'
    
    # API configuration
    api_config_file: str = 'intercom.ini'
    
    # Airtable configuration
    airtable_table: str = "intercom"
    
    # Data validation configuration
    required_columns: List[str] = None
    max_null_percentage: float = 0.1
    
    # Synchronization configuration
    key_fields: List[str] = None
    
    # Intercom API configuration
    intercom_version: str = "2.10"
    batch_size: int = 100
    
    # Data processing configuration
    custom_attributes: List[str] = None
    
    # Logging configuration
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.key_fields is None:
            self.key_fields = ['conversation id']
        
        if self.required_columns is None:
            self.required_columns = ['conversation_id', 'user_id', 'conversation', 'created_at']
        
        if self.custom_attributes is None:
            self.custom_attributes = []
    
    def get_timestamps(self) -> tuple[int, int]:
        """Get start and end timestamps from date strings."""
        import pytz
        
        # Define Central Timezone
        central_tz = pytz.timezone('US/Central')
        
        # Start Date: 00:00:00 Central Time
        start_object = datetime.strptime(self.start_date, '%Y-%m-%d')
        start_of_period = datetime(start_object.year, start_object.month, start_object.day)
        # Localize to Central Time
        start_localized = central_tz.localize(start_of_period)
        start_timestamp = int(start_localized.timestamp())
        
        # End Date: 23:59:59 Central Time (Inclusive)
        end_object = datetime.strptime(self.end_date, '%Y-%m-%d')
        # Set to end of day
        end_of_period = datetime(end_object.year, end_object.month, end_object.day, 23, 59, 59)
        # Localize to Central Time
        end_localized = central_tz.localize(end_of_period)
        end_timestamp = int(end_localized.timestamp())
        
        return start_timestamp, end_timestamp
    
    def validate_config(self) -> bool:
        """Validate configuration parameters."""
        if not self.start_date or not self.end_date:
            raise ValueError("start_date and end_date cannot be empty")
        
        if not self.api_config_file:
            raise ValueError("api_config_file cannot be empty")
        
        if not self.airtable_table:
            raise ValueError("airtable_table cannot be empty")
        
        if self.max_null_percentage < 0 or self.max_null_percentage > 1:
            raise ValueError("max_null_percentage must be between 0 and 1")
        
        # Validate date format
        try:
            datetime.strptime(self.start_date, '%Y-%m-%d')
            datetime.strptime(self.end_date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Date format must be YYYY-MM-DD")
        
        return True
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'intercom_sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stderr),
                logging.FileHandler(log_file)
            ]
        )
        return logging.getLogger(__name__)
