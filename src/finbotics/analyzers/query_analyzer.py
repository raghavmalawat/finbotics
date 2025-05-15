# src/finbotics/analyzers/query_analyzer.py (updated)
import re
from typing import List, Dict, Any
from datetime import datetime
import logging

class QueryAnalyzer:
    """Analyzes queries to determine which tables/tools to search"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Keyword to table mapping for financial data
        self.financial_keyword_mapping = {
            # Multi-table keywords  
            'payment': ['general_ledger', 'expense_summary'],
            'vendor': ['general_ledger', 'expense_summary', 'profit_loss'],
            'expense': ['profit_loss', 'general_ledger', 'expense_summary'],
            'spent': ['expense_summary', 'general_ledger'],
            'total': ['all'],
            
            # Specific table keywords
            'revenue': ['profit_loss'],
            'income': ['profit_loss'], 
            'profit': ['profit_loss'],
            'loss': ['profit_loss'],
            
            'assets': ['balance_sheet'],
            'liability': ['balance_sheet'],
            'equity': ['balance_sheet'],
            'cash': ['balance_sheet', 'general_ledger'],
            
            'transaction': ['general_ledger'],
            'journal': ['general_ledger'],
            
            'supplier': ['expense_summary', 'general_ledger'],
        }
        
        # Keywords that indicate email search is needed
        self.email_keywords = [
            'email', 'happened', 'invoice', 'issue', 'problem', 
            'discussion', 'correspondence', 'message', 'conversation',
            'what ended up', 'update', 'status', 'follow up',
            'ended up happening', 'outcome', 'resolution'
        ]
        
        self.known_vendors = [
            'openai', 'acme', 'cloudnine', 'beta solutions', 'sevenn', 'deel', 'google'
        ]
        
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine search parameters"""
        query_lower = query.lower()
        
        analysis = {
            'original_query': query,
            'query_type': self._detect_query_type(query_lower),
            'intent': self._detect_intent(query_lower),
            'tables': self._determine_tables(query_lower),
            'requires_email_search': self._requires_email_search(query_lower),
            'time_period': self._extract_time_period(query_lower),
            'vendors': self._extract_vendors(query_lower),
            'aggregation': self._detect_aggregation(query_lower),
            'search_tools': self._determine_search_tools(query_lower)
        }
        
        return analysis
    
    def _detect_query_type(self, query: str) -> str:
        """Detect the primary type of query"""
        # Check for email/communication queries first
        if self._requires_email_search(query):
            # Check if it's purely email or mixed
            if self._is_financial_query(query):
                return 'hybrid_financial_email'
            else:
                return 'email_communication'
        
        # Financial query types
        if any(word in query for word in ['spend', 'spent', 'expense', 'cost']):
            return 'expense_analysis'
        elif any(word in query for word in ['runway', 'burn rate', 'cash flow']):
            return 'cash_flow_analysis'
        elif any(word in query for word in ['revenue', 'income', 'sales']):
            return 'revenue_analysis'
        elif any(word in query for word in ['balance', 'assets', 'liability']):
            return 'balance_sheet_analysis'
        else:
            return 'general_financial'
    
    def _detect_intent(self, query: str) -> str:
        """Detect query intent"""
        if self._requires_email_search(query):
            return 'communication_search'
        elif 'how much' in query or 'total' in query:
            return 'aggregation'
        elif 'show' in query or 'list' in query:
            return 'listing'
        elif 'trend' in query:
            return 'trend_analysis'
        elif 'what happened' in query or 'status' in query:
            return 'status_inquiry'
        else:
            return 'general'
    
    def _requires_email_search(self, query: str) -> bool:
        """Determine if query requires email search"""
        # Check for explicit email keywords
        for keyword in self.email_keywords:
            if keyword in query:
                return True
        
        # Check for vendor + invoice/issue pattern
        vendor_issue_pattern = r'(' + '|'.join(self.known_vendors) + r')\s*(invoice|bill|payment|issue|problem)'
        if re.search(vendor_issue_pattern, query, re.IGNORECASE):
            return True
        
        # Check for "what happened to/with" pattern
        happened_pattern = r'what\s+(happened|ended up happening)\s+(to|with)\s+(\w+)'
        if re.search(happened_pattern, query):
            return True
        
        return False
    
    def _is_financial_query(self, query: str) -> bool:
        """Check if query has financial aspects"""
        financial_keywords = [
            'spend', 'spent', 'cost', 'expense', 'revenue', 'balance',
            'total', 'how much', 'amount', 'payment', 'invoice amount'
        ]
        return any(keyword in query for keyword in financial_keywords)
    
    def _determine_search_tools(self, query: str) -> List[str]:
        """Determine which search tools to use"""
        tools = []
        
        if self._requires_email_search(query):
            tools.append('email_search')
        
        if self._is_financial_query(query):
            tools.append('financial_search')
        
        # Default to financial search if no specific tool identified
        if not tools:
            tools.append('financial_search')
        
        return tools
            
    def _determine_tables(self, query: str) -> List[str]:
        """Determine which tables to query for financial data"""
        if not self._is_financial_query(query):
            return []
        
        tables = set()
        
        for word in query.split():
            if word in self.financial_keyword_mapping:
                mapped_tables = self.financial_keyword_mapping[word]
                if 'all' in mapped_tables:
                    return ['profit_loss', 'balance_sheet', 'general_ledger', 'expense_summary']
                tables.update(mapped_tables)
                
        # Context-based rules
        if 'by vendor' in query:
            tables.add('expense_summary')
            
        if any(vendor in query for vendor in self.known_vendors):
            tables.update(['general_ledger', 'expense_summary'])
            
        return list(tables) or ['general_ledger']
        
    def _extract_time_period(self, query: str) -> Dict[str, Any]:
        """Extract time period from query"""
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                  'july', 'august', 'september', 'october', 'november', 'december']
        
        for i, month in enumerate(months):
            if month in query:
                # Extract year if mentioned
                year_match = re.search(r'(\d{4})', query)
                year = year_match.group(1) if year_match else str(datetime.now().year)
                return {'month': i + 1, 'year': int(year)}
        
        # Check for relative periods
        if 'last month' in query:
            current = datetime.now()
            last_month = (current.month - 1) if current.month > 1 else 12
            last_year = current.year if current.month > 1 else (current.year - 1)
            return {'month': last_month, 'year': last_year}
        elif 'this month' in query:
            return {'month': datetime.now().month, 'year': datetime.now().year}
                
        return {}
        
    def _extract_vendors(self, query: str) -> List[str]:
        """Extract vendor names from query"""
        found_vendors = []
        query_lower = query.lower()
        
        for vendor in self.known_vendors:
            if vendor in query_lower:
                found_vendors.append(vendor)
        
        # Also try to extract unknown vendors after common patterns
        patterns = [
            r'vendor\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
            r'(?:on|to|from|with)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, query)
            for match in matches:
                if match.lower() not in self.known_vendors and match not in found_vendors:
                    found_vendors.append(match)
        
        return found_vendors
        
    def _detect_aggregation(self, query: str) -> str:
        """Detect aggregation type"""
        if 'sum' in query or 'total' in query:
            return 'sum'
        elif 'average' in query:
            return 'avg'
        elif 'count' in query:
            return 'count'
        elif 'top' in query or 'biggest' in query:
            return 'top_n'
        else:
            return 'none'