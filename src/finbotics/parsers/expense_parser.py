# src/finbotics/parsers/expense_parser.py
import pandas as pd
import json
from typing import List, Dict, Any
import logging
from src.finbotics.parsers.base_parser import BaseParser
from src.finbotics.db.sqlite_setup import SQLiteSetup

class ExpenseSummaryParser(BaseParser):
    """Parser for Expense Summary by Vendor"""
    
    def __init__(self, db_setup: SQLiteSetup):
        super().__init__(db_setup)
        self.logger = logging.getLogger(__name__)
        
    def parse_expense_summary(self, file_path: str) -> None:
        """Parse Expense Summary file and store in database"""
        self.logger.info(f"Parsing Expense Summary file: {file_path}")
        
        # Read the CSV file
        df = self.read_csv_file(file_path)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Parse the expense summary
        records = self._parse_expense_data(df)
        
        # Clear existing data
        self.db_setup.clear_table('expense_summary')
        
        # Insert new data
        self.db_setup.insert_many('expense_summary', records)
        self.logger.info(f"Inserted {len(records)} records into expense_summary table")
        
    def _parse_expense_data(self, df: pd.DataFrame) -> List[Dict]:
        """Parse expense data from dataframe"""
        records = []
        
        # Identify the structure of the file
        # First column should be vendor name
        vendor_column = df.columns[0]
        
        # Find date columns
        date_columns = self.get_date_columns(df)
        
        # Total column (usually last)
        total_column = None
        for col in df.columns[::-1]:  # Search from end
            if 'total' in col.lower():
                total_column = col
                break
        
        for idx, row in df.iterrows():
            # Skip empty rows
            vendor_name = row[vendor_column]
            if pd.isna(vendor_name) or str(vendor_name).strip() == '':
                continue
            
            # Skip header or separator rows
            if str(vendor_name).strip() in ['Vendor', '-', '=', 'Total']:
                continue
            
            record = {
                'vendor_name': str(vendor_name).strip()
            }
            
            # Parse monthly values
            monthly_values = {}
            for date_col in date_columns:
                if date_col in row.index:
                    date_key = self.parse_date_column(date_col)
                    if date_key:
                        monthly_values[date_key.strftime('%Y-%m')] = self.parse_currency_value(row[date_col])
            
            record['values_json'] = json.dumps(monthly_values)
            
            # Parse total
            if total_column and total_column in row.index:
                record['total'] = self.parse_currency_value(row[total_column])
            else:
                # Calculate total from monthly values
                record['total'] = sum(monthly_values.values())
            
            # Extract additional metadata if available
            # Category (if present in another column)
            category_column = None
            for col in df.columns:
                if 'category' in col.lower():
                    category_column = col
                    break
            
            if category_column and category_column in row.index:
                record['category'] = str(row[category_column]).strip() if pd.notna(row[category_column]) else None
            
            # Try to determine vendor type based on name
            record['vendor_type'] = self._classify_vendor(record['vendor_name'])
            
            records.append(record)
        
        return records
    
    def _classify_vendor(self, vendor_name: str) -> str:
        """Classify vendor based on name patterns"""
        vendor_lower = vendor_name.lower()
        
        # Technology vendors
        tech_keywords = ['software', 'cloud', 'ai', 'tech', 'digital', 'data', 'cyber']
        if any(keyword in vendor_lower for keyword in tech_keywords):
            return 'Technology'
        
        # Professional services
        prof_keywords = ['consulting', 'legal', 'accounting', 'audit', 'advisory']
        if any(keyword in vendor_lower for keyword in prof_keywords):
            return 'Professional Services'
        
        # Insurance
        if 'insurance' in vendor_lower or 'benefit' in vendor_lower:
            return 'Insurance'
        
        # Utilities
        if any(word in vendor_lower for word in ['electric', 'gas', 'water', 'internet', 'telecom']):
            return 'Utilities'
        
        # Default
        return 'Other'
    
    def aggregate_by_category(self) -> Dict[str, float]:
        """Aggregate expenses by category"""
        query = """
            SELECT category, SUM(total) as category_total
            FROM expense_summary
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY category_total DESC
        """
        
        results = self.db_setup.execute_query(query)
        return {row['category']: row['category_total'] for row in results}
    
    def get_top_vendors(self, limit: int = 10) -> List[Dict]:
        """Get top vendors by total spending"""
        query = """
            SELECT vendor_name, category, vendor_type, total, values_json
            FROM expense_summary
            ORDER BY total DESC
            LIMIT ?
        """
        
        results = self.db_setup.execute_query(query, (limit,))
        
        # Parse JSON values
        for result in results:
            result['monthly_values'] = json.loads(result['values_json'])
            
        return results
    
    def get_vendor_trend(self, vendor_name: str) -> Dict[str, float]:
        """Get spending trend for a specific vendor"""
        query = """
            SELECT values_json
            FROM expense_summary
            WHERE vendor_name = ?
        """
        
        results = self.db_setup.execute_query(query, (vendor_name,))
        
        if results:
            return json.loads(results[0]['values_json'])
        return {}
    
    def validate_expense_summary(self) -> Dict[str, Any]:
        """Validate expense summary data"""
        validation_results = {
            'valid': True,
            'issues': [],
            'statistics': {}
        }
        
        try:
            # Get all records
            records = self.db_setup.execute_query("SELECT * FROM expense_summary")
            
            # Basic statistics
            validation_results['statistics']['total_vendors'] = len(records)
            
            if records:
                # Check totals vs monthly values
                import json
                total_mismatches = []
                
                for record in records:
                    vendor_name = record['vendor_name']
                    recorded_total = record.get('total', 0) or 0
                    
                    # Calculate sum from monthly values
                    monthly_values = json.loads(record['values_json'])
                    calculated_total = sum(monthly_values.values())
                    
                    # Check if totals match (allow small difference)
                    if abs(recorded_total - calculated_total) > 0.01:
                        total_mismatches.append({
                            'vendor': vendor_name,
                            'recorded_total': recorded_total,
                            'calculated_total': calculated_total,
                            'difference': recorded_total - calculated_total
                        })
                        validation_results['issues'].append(
                            f"Total mismatch for {vendor_name}: "
                            f"Recorded {recorded_total:.2f}, calculated {calculated_total:.2f}"
                        )
                
                if total_mismatches:
                    validation_results['valid'] = False
                    validation_results['statistics']['total_mismatches'] = len(total_mismatches)
                
                # Category distribution
                category_stats = self.aggregate_by_category()
                validation_results['statistics']['category_distribution'] = category_stats
                
                # Top vendors
                top_vendors = self.get_top_vendors(10)
                validation_results['statistics']['top_vendors'] = [
                    {'vendor': v['vendor_name'], 'total': v['total']}
                    for v in top_vendors
                ]
                
                # Vendor type distribution
                type_query = """
                    SELECT vendor_type, COUNT(*) as count, SUM(total) as total_amount
                    FROM expense_summary
                    WHERE vendor_type IS NOT NULL
                    GROUP BY vendor_type
                    ORDER BY total_amount DESC
                """
                type_stats = self.db_setup.execute_query(type_query)
                validation_results['statistics']['vendor_types'] = {
                    t['vendor_type']: {
                        'count': t['count'],
                        'total': t['total_amount']
                    }
                    for t in type_stats
                }
                
                # Monthly spending pattern
                monthly_totals = {}
                for record in records:
                    monthly_values = json.loads(record['values_json'])
                    for month, amount in monthly_values.items():
                        monthly_totals[month] = monthly_totals.get(month, 0) + amount
                
                validation_results['statistics']['monthly_totals'] = monthly_totals
                
                # Check for vendors with no spending
                zero_spending = [r for r in records if r.get('total', 0) == 0]
                if zero_spending:
                    validation_results['statistics']['vendors_with_no_spending'] = len(zero_spending)
                    
            else:
                validation_results['issues'].append("No expense summary entries found")
                validation_results['valid'] = False
                
        except Exception as e:
            validation_results['valid'] = False
            validation_results['issues'].append(f"Validation error: {str(e)}")
            self.logger.error(f"Error validating expense summary: {str(e)}")
            
        return validation_results

