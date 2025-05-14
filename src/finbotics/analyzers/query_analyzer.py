# src/finbotics/analyzers/query_analyzer.py
import re
from typing import List, Dict, Any
from datetime import datetime
import logging

class QueryAnalyzer:
    """Analyzes queries to determine which tables to search"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Keyword to table mapping
        self.keyword_mapping = {
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
        
        self.known_vendors = [
            'openai', 'acme', 'cloudnine', 'beta solutions'
        ]
        
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze query to determine search parameters"""
        query_lower = query.lower()
        
        analysis = {
            'original_query': query,
            'intent': self._detect_intent(query_lower),
            'tables': self._determine_tables(query_lower),
            'time_period': self._extract_time_period(query_lower),
            'vendors': self._extract_vendors(query_lower),
            'aggregation': self._detect_aggregation(query_lower)
        }
        
        return analysis
        
    def _detect_intent(self, query: str) -> str:
        """Detect query intent"""
        if 'how much' in query or 'total' in query:
            return 'aggregation'
        elif 'show' in query or 'list' in query:
            return 'listing'
        elif 'trend' in query:
            return 'trend_analysis'
        else:
            return 'general'
            
    def _determine_tables(self, query: str) -> List[str]:
        """Determine which tables to query"""
        tables = set()
        
        for word in query.split():
            if word in self.keyword_mapping:
                mapped_tables = self.keyword_mapping[word]
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
                return {'month': i + 1, 'year': 2024}  # Default year
                
        return {}
        
    def _extract_vendors(self, query: str) -> List[str]:
        """Extract vendor names from query"""
        found_vendors = []
        for vendor in self.known_vendors:
            if vendor in query:
                found_vendors.append(vendor)
        return found_vendors
        
    def _detect_aggregation(self, query: str) -> str:
        """Detect aggregation type"""
        if 'sum' in query or 'total' in query:
            return 'sum'
        elif 'average' in query:
            return 'avg'
        elif 'count' in query:
            return 'count'