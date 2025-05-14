# src/finbotics/query_processor.py (updated version)
from typing import Tuple, List, Dict, Any
import json
import re
from datetime import datetime
from src.finbotics.tools.financial_search_tool import FinancialSearchTool
from src.finbotics.analyzers.query_analyzer import QueryAnalyzer
from src.finbotics.db.sqlite_setup import SQLiteSetup
import logging

class QueryProcessor:
    """Processes queries and returns formatted results"""
    
    def __init__(self):
        self.financial_search = FinancialSearchTool()
        self.query_analyzer = QueryAnalyzer()
        self.db_setup = SQLiteSetup()
        self.db_setup.connect()
        self.logger = logging.getLogger(__name__)

    
    def process_query(self, query: str) -> Tuple[str, List[str], bool]:
        """
        Process a query and return result, sources, and data availability
        
        Returns:
            - result: The answer text
            - sources: List of source files used
            - data_found: Whether relevant data was found
        """

        self.logger.info(f"Processing query: {query}")

        try:
            # Search for financial data
            search_result = self.financial_search._run(query)
            self.logger.info(f"Search result: {search_result[:500]}...")  # Log first 500 chars
            
            # Parse the search result
            search_data = json.loads(search_result)
            
            # Log the SQL that was generated
            sql_query = search_data.get('sql_generated', '')
            self.logger.info(f"Generated SQL: {sql_query}")
            
            # Extract the actual results
            results = search_data.get('results', [])
            self.logger.info(f"Query results: {results}")
            
            # Determine sources based on the SQL query
            sources = self._extract_sources_from_sql(sql_query)
            self.logger.info(f"Sources identified: {sources}")
            
            # Check if data was found
            data_found = (
                results != "No results found." and 
                isinstance(results, list) and 
                len(results) > 0
            )
            
            # Format the result for display
            if data_found:
                formatted_result = self._format_results(results, search_data.get('analysis', {}), query)
                self.logger.info(f"Formatted result: {formatted_result}")
            else:
                formatted_result = self._format_no_data_message(query)
                data_found = False
            
            return formatted_result, sources, data_found
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}", exc_info=True)
            error_message = f"Error processing query: {str(e)}"
            return error_message, [], False
    
    def _extract_sources_from_sql(self, sql_query: str) -> List[str]:
        """Extract source table names from SQL query"""
        sources = []
        sql_lower = sql_query.lower()
        
        # Map table names to user-friendly source names
        table_mapping = {
            'expense_summary': 'Expense Summary (expense_summary.csv)',
            'general_ledger': 'General Ledger (general_ledger.csv)',
            'profit_loss': 'Profit & Loss Statement (profit_loss.csv)',
            'balance_sheet': 'Balance Sheet (balance_sheet.csv)'
        }
        
        for table, source_name in table_mapping.items():
            if table in sql_lower:
                sources.append(source_name)
        
        return sources if sources else ['Financial Database']
    
    def _format_no_data_message(self, query: str) -> str:
        """Format a message when no data is found"""
        query_lower = query.lower()
        
        if 'spend' in query_lower or 'spent' in query_lower:
            return "No spending data found for the specified criteria."
        elif 'vendor' in query_lower:
            return "No vendor information found for the specified criteria."
        elif 'expense' in query_lower:
            return "No expense data found for the specified period."
        else:
            return "No data found matching your query."
        
    def _format_results(self, results: List[Dict], analysis: Dict, query: str) -> str:
        """Format results into a readable string"""
        if not results:
            return "No data found for your query."
        
        query_lower = query.lower()

        self.logger.info(f"Formatting results - count: {len(results)}")
        self.logger.info(f"First 3 results: {results[:3]}")
        
        if 'top' in query_lower and 'vendor' in query_lower:
            output = ["Top vendors by spending:"]
            
            # Extract the number requested
            num_match = re.search(r'top\s+(\d+)', query_lower)
            requested_count = int(num_match.group(1)) if num_match else 5
            
            # Ensure we only show the requested number
            vendors_to_show = results[:requested_count]
            
            for i, result in enumerate(vendors_to_show, 1):
                vendor = result.get('vendor_name', 'Unknown')
                total = result.get('total', 0)
                category = result.get('category', 'N/A')
                output.append(f"{i}. {vendor}: ${total:,.2f} (Category: {category})")
            
            return "\n".join(output)
    
        # Handle category spending queries (like Health Insurance)
        if 'insurance' in query_lower or any(cat in query_lower for cat in ['health', 'software', 'rent', 'payroll']):
            if isinstance(results[0], dict) and 'total_spent' in results[0]:
                total = results[0]['total_spent'] or 0
                category = self._extract_category_from_query(query)
                period = self._extract_period_from_query(query)
                return f"Total spending on {category} for {period}: ${total:,.2f}"
        
        # Handle total expense queries
        if 'total' in query_lower and 'expense' in query_lower:
            if isinstance(results[0], dict) and 'total_expenses' in results[0]:
                total = results[0]['total_expenses'] or 0
                period = self._extract_period_from_query(query)
                return f"Total expenses for {period}: ${total:,.2f}"
        
        # Handle vendor spending queries
        if any(word in query_lower for word in ['spend', 'spent']) and 'on' in query_lower:
            if isinstance(results[0], dict) and 'total_spent' in results[0]:
                total = results[0]['total_spent'] or 0
                vendor = self._extract_vendor_from_query(query)
                period = self._extract_period_from_query(query)
                return f"Total spending on {vendor} for {period}: ${total:,.2f}"
            
            # Handle detailed transaction results
            output = []
            for result in results:
                if 'vendor_name' in result:
                    vendor = result['vendor_name']
                    amount = result.get('spent_amount') or result.get('amount') or result.get('total', 0)
                    if amount:
                        output.append(f"{vendor}: ${amount:,.2f}")
                elif 'date' in result and 'description' in result:
                    date = result['date']
                    desc = result['description']
                    amount = result.get('amount') or result.get('credit', 0)
                    vendor = result.get('vendor', 'Unknown')
                    output.append(f"{date} - {desc} ({vendor}): ${amount:,.2f}")
            
            if output:
                return "Spending details:\n" + "\n".join(output)
        
        # ... (keep rest of the existing formatting logic)
        
        # Default formatting for other queries
        return self._default_format_results(results)
    
    def _extract_category_from_query(self, query: str) -> str:
        """Extract category name from query"""
        categories = {
            'health insurance': ['health insurance', 'health benefit'],
            'software': ['software', 'saas'],
            'payroll': ['payroll', 'salary'],
            'rent': ['rent', 'office rent'],
            'utilities': ['utilities', 'electric', 'gas'],
        }
        
        query_lower = query.lower()
        for category, variations in categories.items():
            for variation in variations:
                if variation in query_lower:
                    return category.title()
        
        return "Unknown Category"
    
    def _extract_vendor_from_query(self, query: str) -> str:
        """Extract vendor name from query"""
        vendors = ['openai', 'google', 'amazon', 'microsoft', 'stripe']
        
        query_lower = query.lower()
        for vendor in vendors:
            if vendor in query_lower:
                return vendor.title()
        
        # Try to extract after "on"
        match = re.search(r'on\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*)', query)
        if match:
            return match.group(1)
        
        return "Unknown Vendor"
    
    def _extract_period_from_query(self, query: str) -> str:
        """Extract time period from query"""
        months = {
            'january': 'January', 'february': 'February', 'march': 'March',
            'april': 'April', 'may': 'May', 'june': 'June',
            'july': 'July', 'august': 'August', 'september': 'September',
            'october': 'October', 'november': 'November', 'december': 'December'
        }
        
        query_lower = query.lower()
        
        # Check for specific months
        for month, display in months.items():
            if month in query_lower:
                # Look for year
                year_match = re.search(r'\b(20\d{2})\b', query)
                if year_match:
                    return f"{display} {year_match.group(1)}"
                else:
                    return f"{display} {datetime.now().year}"
        
        # Check for relative periods
        if 'last month' in query_lower:
            last_month = datetime.now().replace(day=1) - timedelta(days=1)
            return last_month.strftime('%B %Y')
        elif 'this month' in query_lower:
            return datetime.now().strftime('%B %Y')
        
        return "the specified period"
    

    def _default_format_results(self, results: List[Dict]) -> str:
        """Default formatting for results"""
        output = []
        
        for result in results[:10]:  # Limit to 10 results
            line_parts = []
            
            # Key fields to display
            key_fields = ['vendor_name', 'category', 'account_name', 'date', 'description']
            value_fields = ['total', 'amount', 'spent_amount', 'debit', 'credit', 'balance', 'total_spent', 'total_expenses']
            
            # Add key fields
            for field in key_fields:
                if field in result and result[field]:
                    line_parts.append(f"{field.replace('_', ' ').title()}: {result[field]}")
            
            # Add value fields
            for field in value_fields:
                if field in result and result[field] is not None:
                    line_parts.append(f"{field.replace('_', ' ').title()}: ${result[field]:,.2f}")
            
            # Handle JSON fields
            if 'values_json' in result and result['values_json']:
                try:
                    values = json.loads(result['values_json'])
                    if values:
                        # Show first few values
                        for k, v in list(values.items())[:3]:
                            line_parts.append(f"{k}: ${v:,.2f}")
                except:
                    pass
            
            if line_parts:
                output.append(" | ".join(line_parts))
        
        return "\n".join(output) if output else "No formatted results available."