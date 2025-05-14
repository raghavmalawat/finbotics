# src/finbotics/tools/financial_aggregator.py
from typing import Dict, Any, List
import json
from datetime import datetime

class FinancialAggregator:
    """Aggregates financial data across multiple tables"""
    
    def __init__(self, db_setup):
        self.db_setup = db_setup
    
    def calculate_total_expenses(self, start_date: str = None, end_date: str = None) -> float:
        """Calculate total expenses for a period"""
        query = """
        SELECT SUM(credit) as total_expenses
        FROM general_ledger
        WHERE credit > 0
        """
        
        params = []
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
            
        results = self.db_setup.execute_query(query, tuple(params))
        return results[0]['total_expenses'] if results else 0.0
    
    def calculate_burn_rate(self, months: int = 3) -> Dict[str, float]:
        """Calculate average monthly burn rate"""
        query = """
        SELECT 
            strftime('%Y-%m', date) as month,
            SUM(credit - debit) as net_outflow
        FROM general_ledger
        WHERE date >= date('now', '-{} months')
        GROUP BY strftime('%Y-%m', date)
        ORDER BY month DESC
        """.format(months)
        
        results = self.db_setup.execute_query(query)
        
        if results:
            monthly_burns = [r['net_outflow'] for r in results]
            avg_burn = sum(monthly_burns) / len(monthly_burns)
            
            return {
                'monthly_burns': {r['month']: r['net_outflow'] for r in results},
                'average_burn_rate': avg_burn,
                'months_analyzed': len(results)
            }
        
        return {'average_burn_rate': 0.0, 'months_analyzed': 0}
    
    def get_vendor_spending_trend(self, vendor_name: str) -> Dict[str, Any]:
        """Get spending trend for a specific vendor"""
        # From expense summary
        query = """
        SELECT values_json
        FROM expense_summary
        WHERE LOWER(vendor_name) LIKE ?
        """
        
        results = self.db_setup.execute_query(query, (f'%{vendor_name.lower()}%',))
        
        if results:
            monthly_values = json.loads(results[0]['values_json'])
            
            # Calculate trend
            sorted_months = sorted(monthly_values.keys())
            values = [monthly_values[month] for month in sorted_months]
            
            trend = 'stable'
            if len(values) > 1:
                if values[-1] > values[0] * 1.1:
                    trend = 'increasing'
                elif values[-1] < values[0] * 0.9:
                    trend = 'decreasing'
            
            return {
                'vendor': vendor_name,
                'monthly_spending': monthly_values,
                'trend': trend,
                'total': sum(values)
            }
        
        return {'vendor': vendor_name, 'monthly_spending': {}, 'trend': 'no data', 'total': 0}