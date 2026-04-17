"""
Configuration management for Chameleon synchronization operations.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import os
import sys


@dataclass
class ChameleonSyncConfig:
    """Configuration class for Chameleon synchronization operations."""
    
    # API configuration
    api_config_file: str = 'chameleon.ini'
    
    # Chameleon API configuration
    chameleon_version: str = "v3"
    
    # Logging configuration
    log_level: str = "INFO"
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        pass
    
    def validate_config(self) -> bool:
        """Validate configuration parameters."""
        if not self.api_config_file:
            raise ValueError("api_config_file cannot be empty")
        
        return True
    
    def setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, f'chameleon_sync_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        
        logging.basicConfig(
            level=getattr(logging, self.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(sys.stderr),
                logging.FileHandler(log_file)
            ]
        )
        return logging.getLogger(__name__)
