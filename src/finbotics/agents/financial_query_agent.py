# src/finbotics/agents/financial_query_agent.py
from crewai import Agent, Task
from src.finbotics.tools.sqlite_query_tool import SQLiteQueryTool
from src.finbotics.tools.nl_to_sql_tool import NaturalLanguageToSQLTool
from src.finbotics.tools.financial_search_tool import FinancialSearchTool

class FinancialQueryAgent:
    """Agent specialized in financial queries"""
    
    def __init__(self):
        self.sql_tool = SQLiteQueryTool()
        self.nl_to_sql_tool = NaturalLanguageToSQLTool()
        self.search_tool = FinancialSearchTool()
    
    def create_agent(self) -> Agent:
        return Agent(
            role="Financial Data Analyst",
            goal="Extract and analyze financial data to answer user queries accurately",
            backstory="""You are a senior financial analyst with expertise in 
            querying financial databases. You can translate natural language 
            questions into SQL queries and provide insightful analysis of the results.""",
            tools=[self.sql_tool, self.nl_to_sql_tool, self.search_tool],
            verbose=True
        )
    
    def create_search_task(self, query: str) -> Task:
        return Task(
            description=f"""
            Answer this financial query: {query}
            
            Steps:
            1. Use the Financial Search Tool to find relevant data
            2. Analyze the results
            3. Provide a clear, concise answer with supporting data
            4. Include any relevant trends or insights
            """,
            expected_output="A comprehensive answer with data and insights",
            agent=self.create_agent()
        )