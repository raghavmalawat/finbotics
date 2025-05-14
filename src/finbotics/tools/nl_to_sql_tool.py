# src/finbotics/tools/nl_to_sql_tool.py (update the query routing logic)
from crewai.tools import BaseTool
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
import re
from datetime import datetime, timedelta

class NLToSQLInput(BaseModel):
    """Input for Natural Language to SQL Tool"""
    natural_language_query: str = Field(description="Natural language financial query")
    context: Dict[str, Any] = Field(default={}, description="Additional context for query")

class NaturalLanguageToSQLTool(BaseTool):
    name: str = "Natural Language to SQL Tool"
    description: str = "Converts natural language queries to SQL queries for the financial database"
    args_schema: Type[BaseModel] = NLToSQLInput
    
    def _run(self, natural_language_query: str, context: Dict[str, Any] = None) -> str:
        """Convert natural language to SQL"""
        query_lower = natural_language_query.lower()
        context = context or {}
        
        # Check if we're looking for specific categories first
        if self._is_category_spending_query(query_lower):
            return self._generate_category_spending_sql(query_lower)
        elif self._is_vendor_spending_query(query_lower):
            return self._generate_vendor_spending_sql(query_lower)
        elif self._is_expense_query(query_lower):
            return self._generate_expense_sql(query_lower)
        elif self._is_revenue_query(query_lower):
            return self._generate_revenue_sql(query_lower)
        elif self._is_balance_query(query_lower):
            return self._generate_balance_sql(query_lower)
        elif self._is_runway_query(query_lower):
            return self._generate_runway_sql(query_lower)
        elif self._is_top_vendors_query(query_lower):
            return self._generate_top_vendors_sql(query_lower)
        else:
            return self._generate_general_ledger_sql(query_lower)
    
    def _get_month_mapping(self) -> Dict[str, str]:
        """Get month name to number mapping"""
        return {
            'january': '01', 'february': '02', 'march': '03', 'april': '04',
            'may': '05', 'june': '06', 'july': '07', 'august': '08',
            'september': '09', 'october': '10', 'november': '11', 'december': '12'
        }
    
    def _is_category_spending_query(self, query: str) -> bool:
        """Check if query is asking about specific categories"""
        categories = [
            'health insurance', 'payroll', 'rent', 'utilities', 'software',
            'hardware', 'marketing', 'travel', 'legal', 'consulting', 
            'office supplies', 'insurance', 'taxes', 'licenses'
        ]
        
        # Check if asking about spending on specific categories
        spend_pattern = r'spend|spent|cost|expense'
        for category in categories:
            if category in query and re.search(spend_pattern, query):
                return True
        
        return False
    
    def _is_vendor_spending_query(self, query: str) -> bool:
        patterns = [
            r'spend.*on.*(?:openai|google|amazon|microsoft|stripe)',
            r'vendor.*spend',
            r'pay.*to.*(?:openai|google|amazon|microsoft|stripe)'
        ]
        return any(re.search(pattern, query) for pattern in patterns)
    
    def _is_expense_query(self, query: str) -> bool:
        return any(word in query for word in ['expense', 'spent', 'cost', 'spend'])
    
    def _is_revenue_query(self, query: str) -> bool:
        return any(word in query for word in ['revenue', 'income', 'earnings'])
    
    def _is_balance_query(self, query: str) -> bool:
        return any(word in query for word in ['balance', 'cash position', 'bank balance'])
    
    def _is_runway_query(self, query: str) -> bool:
        return any(word in query for word in ['runway', 'burn rate', 'cash burn'])
    
    def _is_top_vendors_query(self, query: str) -> bool:
        return 'top' in query and ('vendor' in query or 'supplier' in query)
    
    def _extract_category(self, query: str) -> str:
        """Extract expense category from query"""
        # Map of category variations to standard names
        category_mapping = {
            'health insurance': ['health insurance', 'health benefit', 'health care'],
            'software': ['software', 'saas', 'subscription', 'cloud'],
            'payroll': ['payroll', 'salary', 'wages', 'compensation'],
            'rent': ['rent', 'office rent', 'lease'],
            'utilities': ['utilities', 'electric', 'gas', 'water', 'internet'],
            'insurance': ['insurance', 'liability insurance', 'general insurance'],
            'marketing': ['marketing', 'advertising', 'promotion'],
            'travel': ['travel', 'airfare', 'hotel', 'transportation'],
            'legal': ['legal', 'legal fees', 'attorney'],
            'consulting': ['consulting', 'professional services', 'advisory'],
            'office supplies': ['office supplies', 'supplies', 'stationery'],
            'taxes': ['taxes', 'tax', 'filing fees'],
            'licenses': ['licenses', 'permits', 'registrations', 'licenses and fees']
        }
        
        query_lower = query.lower()
        
        for standard_name, variations in category_mapping.items():
            for variation in variations:
                if variation in query_lower:
                    return standard_name
        
        return None
    
    def _extract_vendor(self, query: str) -> str:
        """Extract vendor name from query"""
        vendors = ['openai', 'google', 'amazon', 'microsoft', 'stripe', 'gusto']
        
        query_lower = query.lower()
        for vendor in vendors:
            if vendor in query_lower:
                return vendor
        
        # Try to extract vendor after "on" or "to"
        patterns = [
            r'(?:on|to|for|from)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
            r'vendor\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_time_period(self, query: str) -> Dict[str, str]:
        result = {}
        month_mapping = self._get_month_mapping()
        
        # Extract month
        for month, num in month_mapping.items():
            if month in query.lower():
                result['month'] = num
                break
        
        # Extract year
        year_match = re.search(r'\b(20\d{2})\b', query)
        if year_match:
            result['year'] = year_match.group(1)
        else:
            # Default to current year
            result['year'] = str(datetime.now().year)
        
        # Handle relative time periods
        if 'last month' in query:
            current = datetime.now()
            first_day_current = current.replace(day=1)
            last_month = first_day_current - timedelta(days=1)
            result['month'] = f"{last_month.month:02d}"
            result['year'] = str(last_month.year)
        elif 'this month' in query:
            current = datetime.now()
            result['month'] = f"{current.month:02d}"
            result['year'] = str(current.year)
        
        return result
    
    def _clean_sql(self, sql: str) -> str:
        """Clean SQL string by removing extra whitespace and newlines"""
        sql = sql.strip()
        sql = re.sub(r'\s+', ' ', sql)
        sql = re.sub(r'\s+,', ',', sql)
        sql = re.sub(r'\(\s+', '(', sql)
        sql = re.sub(r'\s+\)', ')', sql)
        return sql
    
    def _generate_category_spending_sql(self, query: str) -> str:
        """Generate SQL for category-based spending queries (from general ledger)"""
        category = self._extract_category(query)
        time_period = self._extract_time_period(query)

        if category and category.lower() == 'health insurance':
            # Try different variations
            category_conditions = [
                "LOWER(description) LIKE '%health insurance%'",
                "LOWER(description) LIKE '%health%benefit%'",
                "LOWER(description) LIKE '%medical insurance%'",
                "LOWER(vendor) LIKE '%health%'",
                "LOWER(vendor) LIKE '%insurance%'",
                "(LOWER(description) LIKE '%health%' AND LOWER(description) LIKE '%insurance%')"
            ]
        
            where_clause = " OR ".join(category_conditions)

            if time_period.get('month'):
                start_date = f"{time_period['year']}-{time_period['month']}-01"
                end_date = f"{time_period['year']}-{time_period['month']}-31"
                
                sql = f"""SELECT SUM(credit) as total_spent FROM general_ledger WHERE ({where_clause}) AND date >= '{start_date}' AND date <= '{end_date}' AND credit > 0"""
                
                return self._clean_sql(sql)
        
        if category and time_period.get('month'):
            start_date = f"{time_period['year']}-{time_period['month']}-01"
            end_date = f"{time_period['year']}-{time_period['month']}-31"
            
            # Search in general ledger for category spending
            sql = f"""SELECT date, description, vendor, credit as amount FROM general_ledger WHERE LOWER(description) LIKE '%{category.lower()}%' AND date >= '{start_date}' AND date <= '{end_date}' AND credit > 0 ORDER BY date"""
            
            # Also create aggregated version
            sql_aggregate = f"""SELECT SUM(credit) as total_spent FROM general_ledger WHERE LOWER(description) LIKE '%{category.lower()}%' AND date >= '{start_date}' AND date <= '{end_date}' AND credit > 0"""
            
            # Return the aggregate query for total spending
            return self._clean_sql(sql_aggregate)
        elif category:
            # No specific time period, get all spending for category
            sql = f"""SELECT SUM(credit) as total_spent FROM general_ledger WHERE LOWER(description) LIKE '%{category.lower()}%' AND credit > 0"""
            return self._clean_sql(sql)
        else:
            # Fallback to expense summary
            return self._generate_expense_sql(query)
    
    def _generate_vendor_spending_sql(self, query: str) -> str:
        """Generate SQL for vendor-based spending queries"""
        vendor = self._extract_vendor(query)
        time_period = self._extract_time_period(query)
        
        if vendor and time_period.get('month'):
            # First try general ledger for detailed transactions
            start_date = f"{time_period['year']}-{time_period['month']}-01"
            end_date = f"{time_period['year']}-{time_period['month']}-31"
            
            sql = f"""SELECT SUM(credit) as total_spent FROM general_ledger WHERE LOWER(vendor) LIKE '%{vendor.lower()}%' AND date >= '{start_date}' AND date <= '{end_date}' AND credit > 0"""
            return self._clean_sql(sql)
        elif vendor:
            # Try expense summary for vendor totals
            sql = f"""SELECT vendor_name, total FROM expense_summary WHERE LOWER(vendor_name) LIKE '%{vendor.lower()}%'"""
            return self._clean_sql(sql)
        else:
            return self._generate_expense_sql(query)
    
    def _generate_expense_sql(self, query: str) -> str:
        """Generate SQL for general expense queries"""
        time_period = self._extract_time_period(query)
        
        if 'total' in query.lower() and time_period.get('month'):
            # Total expenses for a specific month from general ledger
            start_date = f"{time_period['year']}-{time_period['month']}-01"
            end_date = f"{time_period['year']}-{time_period['month']}-31"
            sql = f"""SELECT SUM(credit) as total_expenses FROM general_ledger WHERE date >= '{start_date}' AND date <= '{end_date}' AND credit > 0"""
            return self._clean_sql(sql)
        else:
            # Fallback to expense summary
            sql = """SELECT vendor_name, category, total FROM expense_summary ORDER BY total DESC LIMIT 20"""
            return self._clean_sql(sql)
    
    def _generate_revenue_sql(self, query: str) -> str:
        """Generate SQL for revenue queries"""
        time_period = self._extract_time_period(query)
        
        if time_period.get('month'):
            date_key = f"{time_period['year']}-{time_period['month']}"
            sql = f"""SELECT category_name, category_path, json_extract(values_json, '$."{date_key}"') as amount FROM profit_loss WHERE category_path LIKE 'Income%' AND is_parent = 0 AND is_total = 0"""
        else:
            sql = """SELECT category_name, category_path, values_json FROM profit_loss WHERE category_path LIKE 'Income%' AND is_parent = 0 AND is_total = 0"""
        
        return self._clean_sql(sql)
    
    def _generate_balance_sql(self, query: str) -> str:
        """Generate SQL for balance queries"""
        sql = """SELECT account_name, account_path, values_json FROM balance_sheet WHERE account_path LIKE '%Cash%' OR account_path LIKE '%Bank%' ORDER BY row_number"""
        return self._clean_sql(sql)
    
    def _generate_runway_sql(self, query: str) -> str:
        """Generate SQL for runway calculation"""
        sql = """SELECT (SELECT json_extract(values_json, '$."2024-01"') FROM balance_sheet WHERE account_path LIKE '%Cash%' LIMIT 1) as current_cash, (SELECT AVG(total) FROM expense_summary WHERE vendor_name != 'TOTAL') as avg_monthly_burn"""
        return self._clean_sql(sql)
    
    def _generate_top_vendors_sql(self, query: str) -> str:
        """Generate SQL for top vendors query"""
        num_match = re.search(r'top\s+(\d+)', query.lower())
        limit = num_match.group(1) if num_match else '5'
        
        # IMPORTANT: Exclude 'TOTAL' row and get the correct number
        sql = f"""SELECT vendor_name, category, total FROM expense_summary WHERE UPPER(vendor_name) != 'TOTAL' ORDER BY total DESC LIMIT {limit}"""
        return self._clean_sql(sql)
    
    def _generate_general_ledger_sql(self, query: str) -> str:
        """Generate SQL for general ledger queries"""
        time_period = self._extract_time_period(query)
        
        if time_period.get('month'):
            start_date = f"{time_period['year']}-{time_period['month']}-01"
            end_date = f"{time_period['year']}-{time_period['month']}-31"
            sql = f"""SELECT date, account_name, description, vendor, debit, credit, balance FROM general_ledger WHERE date >= '{start_date}' AND date <= '{end_date}' ORDER BY date DESC"""
        else:
            sql = """SELECT date, account_name, description, vendor, debit, credit, balance FROM general_ledger ORDER BY date DESC LIMIT 20"""
        
        return self._clean_sql(sql)