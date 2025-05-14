# src/finbotics/queries/hierarchy_queries.py
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

class HierarchyQueryHelper:
    """Helper class for querying hierarchical financial data"""
    
    def __init__(self, db_setup):
        self.db_setup = db_setup
        
    def get_category_with_children(self, table: str, category_name: str) -> List[Dict]:
        """Get a category and all its children"""
        # First, find the category
        name_field = 'category_name' if table == 'profit_loss' else 'account_name'
        path_field = 'category_path' if table == 'profit_loss' else 'account_path'
        
        query = f"""
            SELECT * FROM {table}
            WHERE {name_field} = ?
        """
        parent_records = self.db_setup.execute_query(query, (category_name,))
        
        if not parent_records:
            return []
            
        parent = parent_records[0]
        parent_path = parent[path_field]
        
        # Get all children
        query = f"""
            SELECT * FROM {table}
            WHERE {path_field} LIKE ?
            ORDER BY row_number
        """
        all_records = self.db_setup.execute_query(query, (f"{parent_path}%",))
        
        # Parse JSON values
        for record in all_records:
            record['values'] = json.loads(record['values_json'])
            
        return all_records
    
    def calculate_category_total(self, table: str, category_name: str, 
                               period: Optional[str] = None) -> float:
        """Calculate total for a category including all children"""
        records = self.get_category_with_children(table, category_name)
        
        total = 0.0
        for record in records:
            # Skip parent and total rows for calculation
            if not record['is_parent'] and not record['is_total']:
                values = json.loads(record['values_json'])
                
                if period and period in values:
                    total += values[period]
                elif not period:
                    # Sum all periods
                    total += sum(values.values())
        
        return total
    
    def get_account_balance(self, account_name: str, date: Optional[str] = None) -> float:
        """Get balance for a specific account"""
        query = """
            SELECT values_json FROM balance_sheet
            WHERE account_name = ?
        """
        records = self.db_setup.execute_query(query, (account_name,))
        
        if not records:
            return 0.0
            
        values = json.loads(records[0]['values_json'])
        
        if date and date in values:
            return values[date]
        elif not date:
            # Return the latest balance
            if values:
                latest_date = max(values.keys())
                return values[latest_date]
                
        return 0.0
    
    def get_time_series(self, table: str, category_name: str) -> Dict[str, float]:
        """Get time series data for a category"""
        name_field = 'category_name' if table == 'profit_loss' else 'account_name'
        
        query = f"""
            SELECT values_json FROM {table}
            WHERE {name_field} = ?
        """
        records = self.db_setup.execute_query(query, (category_name,))
        
        if not records:
            return {}
            
        return json.loads(records[0]['values_json'])
    
    def find_categories_by_pattern(self, table: str, pattern: str) -> List[Dict]:
        """Find categories matching a pattern"""
        name_field = 'category_name' if table == 'profit_loss' else 'account_name'
        
        query = f"""
            SELECT * FROM {table}
            WHERE {name_field} LIKE ?
            ORDER BY row_number
        """
        records = self.db_setup.execute_query(query, (f"%{pattern}%",))
        
        for record in records:
            record['values'] = json.loads(record['values_json'])
            
        return records