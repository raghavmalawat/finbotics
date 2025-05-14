# src/finbotics/parsers/base_parser.py
import pandas as pd
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import logging
from pathlib import Path
import json

class BaseParser:
    """Base parser with common functionality for all financial parsers"""
    
    def __init__(self, db_setup: 'SQLiteSetup'):
        self.db_setup = db_setup
        self.logger = logging.getLogger(__name__)

    def parse_date_column(self, column_name: str) -> Optional[datetime]:
        """Parse various date formats from column headers"""
        column_str = str(column_name).strip()
        
        # Skip non-date columns
        if column_str.lower() in ['income', 'total', 'account', 'vendor', 'description', 'category']:
            return None
        
        # Pattern 1: "Jun 14-30, 2024" -> Take end date
        pattern1 = r'(\w+)\s+\d+-(\d+),\s+(\d{4})'
        match1 = re.match(pattern1, column_str)
        if match1:
            month_str, day, year = match1.groups()
            return self._parse_month_year(month_str, year, day)
            
        # Pattern 2: "Jul 2024"
        pattern2 = r'(\w+)\s+(\d{4})'
        match2 = re.match(pattern2, column_str)
        if match2:
            month_str, year = match2.groups()
            return self._parse_month_year(month_str, year)
            
        # Pattern 3: "2024-07" or "2024/07"
        pattern3 = r'(\d{4})[-/](\d{1,2})'
        match3 = re.match(pattern3, column_str)
        if match3:
            year, month = match3.groups()
            return datetime(int(year), int(month), 1)
            
        # Pattern 4: "Jan 2025" format
        pattern4 = r'(\w{3})\s+(\d{4})'
        match4 = re.match(pattern4, column_str)
        if match4:
            month_str, year = match4.groups()
            return self._parse_month_year(month_str, year)
            
        # Pattern 5: Full date "2024-07-31"
        try:
            return pd.to_datetime(column_str)
        except:
            pass
            
        return None
        
    def _parse_month_year(self, month_str: str, year: str, day: str = None) -> Optional[datetime]:
        """Parse month and year into datetime"""
        months = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
            'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        month_lower = month_str.lower()[:3]
        if month_lower in months:
            month_num = months[month_lower]
            year_int = int(year)
            
            if day:
                return datetime(year_int, month_num, int(day))
            else:
                # Return last day of month
                if month_num == 12:
                    return datetime(year_int, 12, 31)
                else:
                    next_month = datetime(year_int, month_num + 1, 1)
                    return next_month - pd.Timedelta(days=1)
                    
        return None
        
    def parse_currency_value(self, value: Any) -> float:
        """Parse currency values, handling various formats"""
        if pd.isna(value) or value == '' or value is None:
            return 0.0
            
        value_str = str(value).strip()
        
        # Remove currency symbols and commas
        value_str = value_str.replace('$', '').replace(',', '').strip()
        
        # Handle parentheses for negative values
        if value_str.startswith('(') and value_str.endswith(')'):
            value_str = '-' + value_str[1:-1].strip()
            
        try:
            return float(value_str)
        except:
            return 0.0
            
    def detect_hierarchy_level(self, cell_value: str) -> Tuple[int, str]:
        """Detect hierarchy level based on indentation"""
        if pd.isna(cell_value):
            return 0, ''
            
        cell_str = str(cell_value)
        
        # Count leading spaces (each 2 spaces = 1 level)
        indent_level = (len(cell_str) - len(cell_str.lstrip())) // 2
        
        # Clean the name
        clean_name = cell_str.strip()
        
        return indent_level, clean_name
        
    def is_parent_row(self, row: pd.Series, date_columns: List[str]) -> bool:
        """Check if a row is a parent category (all values are empty/zero)"""
        for col in date_columns:
            if col in row.index:
                value = self.parse_currency_value(row[col])
                if value != 0:
                    return False
        return True
        
    def is_total_row(self, category_name: str) -> bool:
        """Check if this is a total row"""
        total_indicators = ['total', 'subtotal', 'grand total']
        name_lower = category_name.lower()
        return any(indicator in name_lower for indicator in total_indicators)
        
    def convert_values_to_json(self, row: pd.Series, date_columns: List[str]) -> str:
        """Convert row values to JSON for storage"""
        values = {}
        for col in date_columns:
            if col in row.index:
                date_obj = self.parse_date_column(col)
                if date_obj:
                    date_key = date_obj.strftime('%Y-%m')
                    values[date_key] = self.parse_currency_value(row[col])
        return json.dumps(values)
        
    def read_csv_file(self, file_path: str) -> pd.DataFrame:
        """Read CSV file with proper error handling"""
        try:
            df = pd.read_csv(file_path)
            self.logger.info(f"Successfully read {file_path}")
            return df
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {str(e)}")
            raise
            
    def get_date_columns(self, df: pd.DataFrame) -> List[str]:
        """Identify date columns in the dataframe"""
        date_columns = []
        
        for col in df.columns:
            if self.parse_date_column(col) is not None:
                date_columns.append(col)
                
        return date_columns