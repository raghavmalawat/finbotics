# src/finbotics/parsers/hierarchy_parser.py
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any
import logging
import json
from src.finbotics.parsers.base_parser import BaseParser
from src.finbotics.db.sqlite_setup import SQLiteSetup

class HierarchyParser(BaseParser):
    """Parser for hierarchical financial statements (P&L and Balance Sheet)"""
    
    def __init__(self, db_setup: SQLiteSetup):
        super().__init__(db_setup)
        self.hierarchy_tree = {}
        self.current_path = []
        self.level_stack = []
        
    def parse_profit_loss(self, file_path: str) -> None:
        """Parse P&L statement and store in database"""
        self.logger.info(f"Parsing P&L file: {file_path}")
        
        # Read the CSV file
        df = self.read_csv_file(file_path)
        
        # Get date columns
        date_columns = self.get_date_columns(df)
        self.logger.info(f"Found date columns: {date_columns}")
        
        # Parse the hierarchical structure
        records = self._parse_hierarchical_data(df, date_columns, 'profit_loss')
        
        # Clear existing data
        self.db_setup.clear_table('profit_loss')
        
        # Insert new data
        self.db_setup.insert_many('profit_loss', records)
        self.logger.info(f"Inserted {len(records)} records into profit_loss table")
        
    def parse_balance_sheet(self, file_path: str) -> None:
        """Parse Balance Sheet and store in database"""
        self.logger.info(f"Parsing Balance Sheet file: {file_path}")
        
        # Read the CSV file
        df = self.read_csv_file(file_path)
        
        # Get date columns
        date_columns = self.get_date_columns(df)
        self.logger.info(f"Found date columns: {date_columns}")
        
        # Parse the hierarchical structure
        records = self._parse_hierarchical_data(df, date_columns, 'balance_sheet')
        
        # Clear existing data
        self.db_setup.clear_table('balance_sheet')
        
        # Insert new data
        self.db_setup.insert_many('balance_sheet', records)
        self.logger.info(f"Inserted {len(records)} records into balance_sheet table")
        
    def _parse_hierarchical_data(self, df: pd.DataFrame, date_columns: List[str], 
                                table_type: str) -> List[Dict]:
        """Parse hierarchical data from dataframe"""
        records = []
        self.hierarchy_tree = {}
        self.current_path = []
        self.level_stack = []
        
        # First column should contain category/account names
        category_column = df.columns[0]
        
        # Track parent categories
        parent_stack = []
        current_parents = {}  # level -> parent name
        
        for idx, row in df.iterrows():
            # Skip completely empty rows
            if pd.isna(row[category_column]) or str(row[category_column]).strip() == '':
                continue
                
            # Get hierarchy level and clean name
            level, category_name = self.detect_hierarchy_level(row[category_column])
            
            if not category_name:
                continue
                
            # Update parent tracking
            current_parents[level] = category_name
            
            # Determine parent category
            parent_category = None
            if level > 0:
                # Find the nearest parent at a lower level
                for parent_level in range(level - 1, -1, -1):
                    if parent_level in current_parents:
                        parent_category = current_parents[parent_level]
                        break
            
            # Build category path
            path_components = []
            for path_level in range(level + 1):
                if path_level in current_parents:
                    path_components.append(current_parents[path_level])
            category_path = '/'.join(path_components)
            
            # Check if this is a parent or total row
            is_parent = self.is_parent_row(row, date_columns)
            is_total = self.is_total_row(category_name)
            
            # Determine line type
            if is_parent and not is_total:
                line_type = 'parent'
            elif is_total:
                line_type = 'total'
            else:
                line_type = 'detail'
            
            # Convert values to JSON
            values_json = self.convert_values_to_json(row, date_columns)
            
            # Create record based on table type
            if table_type == 'profit_loss':
                record = {
                    'category_name': category_name,
                    'category_path': category_path,
                    'parent_category': parent_category,
                    'level': level,
                    'is_parent': is_parent,
                    'is_total': is_total,
                    'line_type': line_type,
                    'values_json': values_json,
                    'row_number': idx,
                    'indentation_level': level
                }
            else:  # balance_sheet
                # Determine account type based on top-level category
                account_type = self._determine_account_type(category_path)
                
                record = {
                    'account_name': category_name,
                    'account_path': category_path,
                    'account_type': account_type,
                    'parent_account': parent_category,
                    'level': level,
                    'is_parent': is_parent,
                    'is_total': is_total,
                    'values_json': values_json,
                    'row_number': idx
                }
            
            records.append(record)
            
            # Clean up parent tracking when we exit a section
            if is_total:
                # Remove parents at current level and above
                levels_to_remove = [l for l in current_parents.keys() if l >= level]
                for l in levels_to_remove:
                    if l in current_parents:
                        del current_parents[l]
        
        return records
    
    def _determine_account_type(self, account_path: str) -> str:
        """Determine account type from the path"""
        path_lower = account_path.lower()
        
        if 'asset' in path_lower:
            return 'asset'
        elif 'liabilit' in path_lower:
            return 'liability'
        elif 'equity' in path_lower:
            return 'equity'
        else:
            # Default based on common patterns
            if any(term in path_lower for term in ['cash', 'receivable', 'inventory', 'prepaid']):
                return 'asset'
            elif any(term in path_lower for term in ['payable', 'debt', 'loan']):
                return 'liability'
            else:
                return 'equity'
    
    def validate_hierarchy(self, table_name: str) -> Dict[str, Any]:
        """Validate the parsed hierarchy for consistency"""
        validation_results = {
            'valid': True,
            'issues': [],
            'statistics': {}
        }
        
        # Get all records
        records = self.db_setup.execute_query(f"SELECT * FROM {table_name}")
        
        # Basic statistics
        validation_results['statistics']['total_records'] = len(records)
        validation_results['statistics']['max_level'] = max(r['level'] for r in records)
        
        # Check for orphaned children
        parent_names = set()
        child_parent_pairs = []
        
        for record in records:
            if record['level'] == 0:
                parent_names.add(record['category_name' if table_name == 'profit_loss' else 'account_name'])
            else:
                parent = record['parent_category' if table_name == 'profit_loss' else 'parent_account']
                if parent:
                    child_parent_pairs.append((record['category_name' if table_name == 'profit_loss' else 'account_name'], parent))
                    parent_names.add(parent)
        
        # Find orphans
        for child, parent in child_parent_pairs:
            if parent not in [r['category_name' if table_name == 'profit_loss' else 'account_name'] for r in records]:
                validation_results['issues'].append(f"Orphaned child: {child} (parent: {parent} not found)")
                validation_results['valid'] = False
        
        # Check totals match sum of children (for P&L)
        if table_name == 'profit_loss':
            total_records = [r for r in records if r['is_total']]
            for total_record in total_records:
                # This would require more complex logic to sum children
                # For now, just flag that validation should be done
                validation_results['statistics']['total_rows'] = len(total_records)
        
        return validation_results