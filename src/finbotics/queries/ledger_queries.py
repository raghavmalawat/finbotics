# src/finbotics/queries/ledger_queries.py
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class LedgerQueryHelper:
    """Helper class for querying general ledger data"""
    
    def __init__(self, db_setup):
        self.db_setup = db_setup
        
    def get_transactions_by_vendor(self, vendor_name: str, 
                                  start_date: Optional[str] = None,
                                  end_date: Optional[str] = None) -> List[Dict]:
        """Get all transactions for a specific vendor"""
        query = """
            SELECT * FROM general_ledger
            WHERE vendor LIKE ?
        """
        params = [f"%{vendor_name}%"]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
            
        query += " ORDER BY date DESC"
        
        return self.db_setup.execute_query(query, tuple(params))
    
    def get_account_transactions(self, account_name: str,
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> List[Dict]:
        """Get all transactions for a specific account"""
        query = """
            SELECT * FROM general_ledger
            WHERE account_name LIKE ?
        """
        params = [f"%{account_name}%"]
        
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
            
        query += " ORDER BY date"
        
        return self.db_setup.execute_query(query, tuple(params))
    
    def calculate_account_balance(self, account_name: str,
                                as_of_date: Optional[str] = None) -> float:
        """Calculate account balance as of a specific date"""
        query = """
            SELECT SUM(debit - credit) as balance
            FROM general_ledger
            WHERE account_name LIKE ?
        """
        params = [f"%{account_name}%"]
        
        if as_of_date:
            query += " AND date <= ?"
            params.append(as_of_date)
            
        result = self.db_setup.execute_query(query, tuple(params))
        return result[0]['balance'] if result and result[0]['balance'] else 0.0
    
    def get_monthly_summary(self, year: int, month: int) -> Dict[str, Any]:
        """Get monthly summary of transactions"""
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"
        
        query = """
            SELECT 
                COUNT(*) as transaction_count,
                SUM(debit) as total_debits,
                SUM(credit) as total_credits,
                COUNT(DISTINCT vendor) as unique_vendors,
                COUNT(DISTINCT account_name) as unique_accounts
            FROM general_ledger
            WHERE date >= ? AND date < ?
        """
        
        result = self.db_setup.execute_query(query, (start_date, end_date))
        return result[0] if result else {}
    
    def find_transactions_by_amount(self, amount: float, 
                                   tolerance: float = 0.01) -> List[Dict]:
        """Find transactions matching a specific amount"""
        query = """
            SELECT * FROM general_ledger
            WHERE (ABS(debit - ?) <= ? OR ABS(credit - ?) <= ?)
            ORDER BY date DESC
        """
        
        return self.db_setup.execute_query(query, (amount, tolerance, amount, tolerance))


class ExpenseQueryHelper:
    """Helper class for querying expense summary data"""
    
    def __init__(self, db_setup):
        self.db_setup = db_setup
        
    def get_vendor_summary(self, vendor_name: str) -> Dict[str, Any]:
        """Get complete summary for a vendor"""
        query = """
            SELECT * FROM expense_summary
            WHERE vendor_name LIKE ?
        """
        
        results = self.db_setup.execute_query(query, (f"%{vendor_name}%",))
        
        if results:
            result = results[0]
            import json
            result['monthly_values'] = json.loads(result['values_json'])
            return result
        return None
    
    def get_vendors_by_category(self, category: str) -> List[Dict]:
        """Get all vendors in a specific category"""
        query = """
            SELECT vendor_name, total, vendor_type
            FROM expense_summary
            WHERE category = ?
            ORDER BY total DESC
        """
        
        return self.db_setup.execute_query(query, (category,))
    
    def calculate_category_trend(self, category: str) -> Dict[str, float]:
        """Calculate spending trend for a category"""
        query = """
            SELECT values_json
            FROM expense_summary
            WHERE category = ?
        """
        
        results = self.db_setup.execute_query(query, (category,))
        
        # Aggregate monthly values
        monthly_totals = {}
        import json
        
        for result in results:
            values = json.loads(result['values_json'])
            for month, amount in values.items():
                monthly_totals[month] = monthly_totals.get(month, 0) + amount
        
        return monthly_totals
    
    def find_vendors_above_threshold(self, threshold: float) -> List[Dict]:
        """Find vendors with spending above a threshold"""
        query = """
            SELECT vendor_name, category, total
            FROM expense_summary
            WHERE total > ?
            ORDER BY total DESC
        """
        
        return self.db_setup.execute_query(query, (threshold,))