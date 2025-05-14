# src/finbotics/tools/financial_search_tool.py
from crewai.tools import BaseTool
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field
import json

class FinancialSearchInput(BaseModel):
    """Input for Financial Search Tool"""
    query: str = Field(description="Natural language financial query")
    include_context: bool = Field(default=True, description="Include contextual information")

class FinancialSearchTool(BaseTool):
    name: str = "Financial Search Tool"
    description: str = "Searches financial data using natural language queries"
    args_schema: Type[BaseModel] = FinancialSearchInput
    
    def _run(self, query: str, include_context: bool = True) -> str:
        """Execute financial search"""
        try:
            # Import tools here to avoid circular dependency
            from src.finbotics.tools.sqlite_query_tool import SQLiteQueryTool
            from src.finbotics.tools.nl_to_sql_tool import NaturalLanguageToSQLTool
            from src.finbotics.analyzers.query_analyzer import QueryAnalyzer
            
            sql_tool = SQLiteQueryTool()
            nl_to_sql = NaturalLanguageToSQLTool()
            query_analyzer = QueryAnalyzer()
            
            # Analyze the query
            analysis = query_analyzer.analyze_query(query)
            
            # Convert to SQL
            sql_query = nl_to_sql._run(query)
            
            # Execute SQL
            results = sql_tool._run(sql_query)
            
            # Parse results if they're JSON
            try:
                results_data = json.loads(results)
            except:
                results_data = results
            
            # Format the response
            response = {
                'query': query,
                'analysis': analysis,
                'sql_generated': sql_query,
                'results': results_data
            }
            
            # Add context if requested
            if include_context and isinstance(results_data, list) and results_data:
                response['context'] = self._add_context(results_data, analysis)
            
            return json.dumps(response, indent=2, default=str)
            
        except Exception as e:
            return json.dumps({
                'error': str(e),
                'query': query
            })
    
    def _add_context(self, results: List[Dict], analysis: Dict) -> Dict:
        """Add contextual information to results"""
        context = {}
        
        # If it's vendor data, add spending trends
        if analysis.get('intent') == 'vendor_spending' and results:
            context['total_vendors'] = len(results)
            context['total_spending'] = sum(r.get('total', 0) for r in results if isinstance(r.get('total'), (int, float)))
            
        # If it's time-based, add period comparisons
        if analysis.get('time_period'):
            context['time_period'] = analysis['time_period']
            
        return context