from crewai.tools import BaseTool
from typing import Type, Dict, List
from pydantic import BaseModel, Field
import re
from datetime import datetime
from dateutil import parser
import calendar

class QueryAnalyzerInput(BaseModel):
    """Input schema for Query Analyzer Tool"""
    query: str = Field(description="User's natural language query")

class QueryAnalyzerTool(BaseTool):
    name: str = "Query Analyzer Tool"
    description: str = "Analyzes queries to extract entities, dates, and determine routing"
    args_schema: Type[BaseModel] = QueryAnalyzerInput
    
    def _run(self, query: str) -> str:
        """Analyze the query and extract components"""
        try:
            analysis = {
                "query_type": self._determine_query_type(query),
                "entities": self._extract_entities(query),
                "time_period": self._extract_time_period(query),
                "comparison_needed": self._needs_comparison(query),
                "email_search_needed": self._needs_email_search(query),
                "aggregation_type": self._get_aggregation_type(query)
            }
            
            # Determine which agents to involve
            agents_needed = self._determine_agents(analysis)
            analysis["agents_needed"] = agents_needed
            
            # Format as string for agent consumption
            result = f"Query Analysis:\n"
            result += f"Type: {analysis['query_type']}\n"
            result += f"Entities: {', '.join(analysis['entities'])}\n"
            result += f"Time Period: {analysis['time_period']}\n"
            result += f"Agents Needed: {', '.join(agents_needed)}\n"
            
            if analysis['comparison_needed']:
                result += "Comparison: Period-over-period comparison required\n"
            if analysis['email_search_needed']:
                result += "Email Search: Required for context\n"
                
            return result
            
        except Exception as e:
            return f"Error analyzing query: {str(e)}"
    
    def _determine_query_type(self, query: str) -> str:
        """Determine the type of query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['spend', 'spent', 'expense', 'cost']):
            return "expense_analysis"
        elif any(word in query_lower for word in ['runway', 'burn rate', 'cash flow']):
            return "cash_flow_analysis"
        elif any(word in query_lower for word in ['invoice', 'email', 'discussion']):
            return "vendor_inquiry"
        elif any(word in query_lower for word in ['spike', 'increase', 'fluctuation', 'change']):
            return "trend_analysis"
        elif any(word in query_lower for word in ['biggest', 'top', 'largest', 'recurring']):
            return "ranking_analysis"
        else:
            return "general_inquiry"
    
    def _extract_entities(self, query: str) -> List[str]:
        """Extract vendor names and categories"""
        entities = []
        
        # Common vendors (extend this list based on your data)
        vendors = ['OpenAI', 'Sevenn', 'AWS', 'Google', 'Microsoft', 'Uber']
        for vendor in vendors:
            if vendor.lower() in query.lower():
                entities.append(vendor)
        
        # Common expense categories
        categories = ['Health Insurance', 'Software', 'Licenses', 'Fees', 'Travel', 'Marketing']
        for category in categories:
            if category.lower() in query.lower():
                entities.append(category)
                
        return entities
    
    def _extract_time_period(self, query: str) -> str:
        """Extract time period from query"""
        query_lower = query.lower()
        
        # Month names
        months = ['january', 'february', 'march', 'april', 'may', 'june',
                  'july', 'august', 'september', 'october', 'november', 'december']
        
        for month in months:
            if month in query_lower:
                # Assume current year or specify logic for year
                return f"{month.capitalize()} 2024"
        
        # Relative time periods
        if 'last month' in query_lower:
            return "Previous month"
        elif 'this month' in query_lower:
            return "Current month"
        elif 'last quarter' in query_lower:
            return "Previous quarter"
        elif 'this year' in query_lower:
            return "Current year"
            
        return "Not specified"
    
    def _needs_comparison(self, query: str) -> bool:
        """Check if query needs period comparison"""
        comparison_words = ['compare', 'versus', 'vs', 'between', 'from', 'to', 
                           'change', 'fluctuation', 'spike', 'increase', 'decrease']
        return any(word in query.lower() for word in comparison_words)
    
    def _needs_email_search(self, query: str) -> bool:
        """Check if query needs email search"""
        email_words = ['email', 'discussion', 'correspondence', 'happened', 
                      'invoice', 'issue', 'problem']
        return any(word in query.lower() for word in email_words)
    
    def _get_aggregation_type(self, query: str) -> str:
        """Determine aggregation type needed"""
        if any(word in query.lower() for word in ['total', 'sum', 'how much']):
            return "sum"
        elif any(word in query.lower() for word in ['average', 'mean']):
            return "average"
        elif any(word in query.lower() for word in ['biggest', 'largest', 'top']):
            return "top_n"
        elif any(word in query.lower() for word in ['trend', 'pattern']):
            return "trend"
        return "none"
    
    def _determine_agents(self, analysis: Dict) -> List[str]:
        """Determine which agents are needed"""
        agents = []
        
        if analysis['query_type'] in ['expense_analysis', 'ranking_analysis']:
            agents.append('expense_analyst')
        if analysis['query_type'] == 'cash_flow_analysis':
            agents.append('cash_flow_analyst')
        if analysis['email_search_needed']:
            agents.append('email_context_agent')
        if analysis['comparison_needed'] or analysis['query_type'] == 'trend_analysis':
            agents.append('expense_analyst')
            agents.append('data_aggregation_agent')
            
        # Always include report generator for formatting
        agents.append('report_generator')
        
        return list(set(agents))  # Remove duplicates