"""
Data validation and quality assurance utilities.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import logging


class DataValidator:
    """Class for validating data quality and structure."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize validator with optional logger."""
        self.logger = logger or logging.getLogger(__name__)
    
    def validate_dataframe_structure(self, df: pd.DataFrame, required_columns: List[str]) -> bool:
        """Validate that DataFrame has required columns."""
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        return True
    
    def check_null_percentage(self, df: pd.DataFrame, column: str, max_percentage: float = 0.1) -> bool:
        """Check if null percentage in column exceeds threshold."""
        if column not in df.columns:
            self.logger.warning(f"Column {column} not found in DataFrame")
            return True
        
        null_count = df[column].isnull().sum()
        null_percentage = null_count / len(df)
        
        if null_percentage > max_percentage:
            self.logger.warning(f"High null percentage in {column}: {null_percentage:.2%}")
            return False
        
        return True
    
    def check_duplicates(self, df: pd.DataFrame, columns: List[str]) -> Tuple[bool, int]:
        """Check for duplicate rows based on specified columns."""
        duplicates = df.duplicated(subset=columns, keep=False)
        duplicate_count = duplicates.sum()
        
        if duplicate_count > 0:
            self.logger.warning(f"Found {duplicate_count} duplicate rows based on columns {columns}")
            return False, duplicate_count
        
        return True, 0
    
    def validate_email_format(self, df: pd.DataFrame, email_column: str = 'email') -> bool:
        """Validate email format using basic regex."""
        if email_column not in df.columns:
            return True
        
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        invalid_emails = df[email_column].dropna().apply(
            lambda x: not bool(re.match(email_pattern, str(x)))
        ).sum()
        
        if invalid_emails > 0:
            self.logger.warning(f"Found {invalid_emails} invalid email formats")
            return False
        
        return True
    
    def validate_data_types(self, df: pd.DataFrame, expected_types: Dict[str, str]) -> bool:
        """Validate that columns have expected data types."""
        for column, expected_type in expected_types.items():
            if column not in df.columns:
                continue
            
            actual_type = str(df[column].dtype)
            if expected_type not in actual_type:
                self.logger.warning(f"Column {column} has type {actual_type}, expected {expected_type}")
                return False
        
        return True
    
    def check_data_consistency(self, df: pd.DataFrame, rules: Dict[str, Any]) -> bool:
        """Check data consistency against business rules."""
        for rule_name, rule_func in rules.items():
            try:
                if not rule_func(df):
                    self.logger.warning(f"Data consistency rule failed: {rule_name}")
                    return False
            except Exception as e:
                self.logger.error(f"Error checking rule {rule_name}: {str(e)}")
                return False
        
        return True
    
    def generate_data_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate a comprehensive data quality report."""
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'null_counts': df.isnull().sum().to_dict(),
            'duplicate_rows': df.duplicated().sum(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'data_types': df.dtypes.to_dict()
        }
        
        # Calculate null percentages
        report['null_percentages'] = {
            col: (df[col].isnull().sum() / len(df)) * 100 
            for col in df.columns
        }
        
        return report


class DataProcessor:
    """Class for data processing and transformation utilities."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize processor with optional logger."""
        self.logger = logger or logging.getLogger(__name__)
    
    def clean_string_columns(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Clean string columns by stripping whitespace and handling nulls."""
        df_clean = df.copy()
        
        for col in columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
                df_clean[col] = df_clean[col].replace(['nan', 'None', '<NA>'], '')
        
        return df_clean
    
    def standardize_datetime_columns(self, df: pd.DataFrame, columns: List[str]) -> pd.DataFrame:
        """Standardize datetime columns to consistent format."""
        df_clean = df.copy()
        
        for col in columns:
            if col in df_clean.columns:
                try:
                    df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
                    df_clean[col] = df_clean[col].dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    self.logger.warning(f"Could not standardize datetime column {col}: {str(e)}")
        
        return df_clean
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'fillna', 
                            fill_value: Any = None, columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Handle missing values using specified strategy."""
        df_clean = df.copy()
        
        if columns is None:
            columns = df_clean.columns
        
        for col in columns:
            if col not in df_clean.columns:
                continue
            
            if strategy == 'fillna':
                if fill_value is not None:
                    df_clean[col] = df_clean[col].fillna(fill_value)
                else:
                    # Use appropriate default based on data type
                    if df_clean[col].dtype in ['int64', 'float64']:
                        df_clean[col] = df_clean[col].fillna(0)
                    else:
                        df_clean[col] = df_clean[col].fillna('')
            elif strategy == 'dropna':
                df_clean = df_clean.dropna(subset=[col])
        
        return df_clean
    
    def remove_duplicates(self, df: pd.DataFrame, subset: Optional[List[str]] = None, 
                         keep: str = 'first') -> pd.DataFrame:
        """Remove duplicate rows from DataFrame."""
        if subset is None:
            subset = df.columns
        
        initial_count = len(df)
        df_clean = df.drop_duplicates(subset=subset, keep=keep)
        removed_count = initial_count - len(df_clean)
        
        if removed_count > 0:
            self.logger.info(f"Removed {removed_count} duplicate rows")
        
        return df_clean
    
    def validate_and_clean_data(self, df: pd.DataFrame, 
                               required_columns: List[str],
                               string_columns: Optional[List[str]] = None,
                               datetime_columns: Optional[List[str]] = None) -> pd.DataFrame:
        """Comprehensive data validation and cleaning."""
        # Validate structure
        validator = DataValidator(self.logger)
        validator.validate_dataframe_structure(df, required_columns)
        
        # Clean data
        df_clean = df.copy()
        
        if string_columns:
            df_clean = self.clean_string_columns(df_clean, string_columns)
        
        if datetime_columns:
            df_clean = self.standardize_datetime_columns(df_clean, datetime_columns)
        
        # Handle missing values
        df_clean = self.handle_missing_values(df_clean)
        
        # Remove duplicates
        df_clean = self.remove_duplicates(df_clean, subset=required_columns)
        
        return df_clean
