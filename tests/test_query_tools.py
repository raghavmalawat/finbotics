# tests/test_query_tools.py
from src.finbotics.tools.financial_search_tool import FinancialSearchTool
from src.finbotics.tools.nl_to_sql_tool import NaturalLanguageToSQLTool
from src.finbotics.agents.financial_query_agent import FinancialQueryAgent
from src.finbotics.db.sqlite_setup import SQLiteSetup
import json

def test_financial_search():
    """Test financial search tool"""
    search_tool = FinancialSearchTool()
    
    queries = [
        "Show me top 5 vendors by spending",
        "What are my total expenses for last month?",
        "How much did I spend on software?",
    ]
    
    print("\n\n=== Financial Search Tests ===")
    for query in queries:
        result = search_tool._run(query)
        print(f"\nQuery: {query}")
        print(f"Result: {result[:500]}...")  # Truncate for readability

def test_financial_agent():
    """Test financial query agent"""
    agent = FinancialQueryAgent()
    
    query = "What are my top 3 vendors and how much did I spend on each?"
    task = agent.create_search_task(query)
    
    print("\n\n=== Financial Agent Test ===")
    print(f"Query: {query}")
    
    # Execute task (this would normally be done by CrewAI)
    # For testing, we'll just show the task configuration
    print(f"Task Description: {task.description}")
    print(f"Expected Output: {task.expected_output}")

def test_nl_to_sql():
    """Test natural language to SQL conversion"""
    nl_to_sql = NaturalLanguageToSQLTool()
    
    queries = [
        "How much did I spend on OpenAI in February?",
        "Show me top 5 vendors by spending",
        "What's my current cash balance?",
        "What are my biggest expenses last month?",
        "Calculate my runway",
        "What are my total expenses for last month?",  # Should include date filter
        "How much did I spend on software?",  # Should filter by category
    ]
    
    print("=== Natural Language to SQL Tests ===")
    for query in queries:
        sql = nl_to_sql._run(query)
        print(f"\nQuery: {query}")
        print(f"SQL: {sql}")

if __name__ == "__main__":
    test_nl_to_sql()
    test_financial_search()
    test_financial_agent()