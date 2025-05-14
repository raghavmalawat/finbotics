# test_end_to_end.py
from src.finbotics.crew import Finbotics
from crewai import Crew, Task

def test_complete_expense_flow():
    """Test the complete flow from query to report"""
    
    finbotics = Finbotics()
    
    # Create a complete flow for expense analysis
    query = "How much did I spend on OpenAI in February?"
    
    # Task 1: Classify the query
    classification_task = Task(
        description=f"""
            Analyze this financial query: "{query}"
            
            Identify the query type, entities mentioned, and time period.
        """,
        expected_output="Query classification with type, vendor, and time period",
        agent=finbotics.query_classifier()
    )
    
    # Task 2: Route to appropriate agent
    routing_task = Task(
        description=f"""
            Based on the classification, route this query to the appropriate agent.
            The query is asking about expenses for a specific vendor in a specific time period.
        """,
        expected_output="Routing decision with target agent and parameters",
        agent=finbotics.query_router(),
        context=[classification_task]
    )
    
    # Task 3: Analyze expenses
    expense_analysis_task = Task(
        description="""
            Analyze expenses for vendor: OpenAI
            Time period: February 2024
            
            Search the general ledger and expense summary for all OpenAI transactions.
            Calculate total spending and list individual transactions.
        """,
        expected_output="Detailed expense analysis with totals and transactions",
        agent=finbotics.expense_analyst()
    )
    
    # Task 4: Generate report
    report_task = Task(
        description="""
            Create a professional expense report based on the OpenAI expense analysis.
            Include executive summary, detailed findings, and source citations.
        """,
        expected_output="Polished expense report with all findings",
        agent=finbotics.report_generator(),
        context=[expense_analysis_task]
    )
    
    # Task 5: Final synthesis
    final_response_task = Task(
        description=f"""
            Create a final response for the user's query: "{query}"
            
            Synthesize all findings into a clear, direct answer.
        """,
        expected_output="Final response that directly answers the user's question",
        agent=finbotics.report_generator(),
        context=[report_task]
    )
    
    # Create crew with all tasks
    crew = Crew(
        agents=[
            finbotics.query_classifier(),
            finbotics.query_router(),
            finbotics.expense_analyst(),
            finbotics.report_generator()
        ],
        tasks=[
            classification_task,
            routing_task,
            expense_analysis_task,
            report_task,
            final_response_task
        ],
        process="sequential",
        verbose=True
    )
    
    result = crew.kickoff()
    print("\n" + "="*60)
    print("FINAL RESULT:")
    print("="*60)
    print(result)
    
    return result

def test_simple_report_generation():
    """Test just the report generation component"""
    
    finbotics = Finbotics()
    
    # Mock expense data
    mock_expense_data = """
    Vendor: OpenAI
    Period: February 2024
    Total Spent: $5,432.00
    
    Transactions:
    - Feb 5: API Usage - $1,200.00
    - Feb 12: API Usage - $1,532.00
    - Feb 19: API Usage - $1,400.00
    - Feb 26: API Usage - $1,300.00
    """
    
    report_task = Task(
        description=f"""
        Create a professional expense report with this data:
        {mock_expense_data}
        
        Include executive summary and source citations.
        """,
        expected_output="Professional expense report",
        agent=finbotics.report_generator()
    )
    
    crew = Crew(
        agents=[finbotics.report_generator()],
        tasks=[report_task],
        process="sequential",
        verbose=True
    )
    
    result = crew.kickoff()
    print(f"\nReport Result: {result}")

def test_multi_agent_coordination():
    """Test coordination between multiple agents"""
    
    finbotics = Finbotics()
    queries = [
        "What are my biggest expenses last month?",
        "Show me software spending trends",
        "How much did we spend on all cloud services?"
    ]
    
    for query in queries:
        print(f"\n\n{'='*60}")
        print(f"Processing: {query}")
        print('='*60)
        
        # Dynamic task creation based on query
        tasks = []
        
        # Always start with classification
        classify_task = Task(
            description=f'Classify this query: "{query}"',
            expected_output="Query classification",
            agent=finbotics.query_classifier()
        )
        tasks.append(classify_task)
        
        # Add appropriate analysis task
        if "biggest expenses" in query.lower():
            analysis_task = Task(
                description="Find the top 5 expense categories from last month",
                expected_output="Top expense categories with amounts",
                agent=finbotics.expense_analyst()
            )
        elif "trending" in query.lower() or "trends" in query.lower():
            analysis_task = Task(
                description="Analyze software spending trends over the past 3 months",
                expected_output="Spending trends analysis",
                agent=finbotics.expense_analyst()
            )
        else:
            analysis_task = Task(
                description="Analyze spending on cloud services (AWS, GCP, Azure, etc.)",
                expected_output="Cloud services expense analysis",
                agent=finbotics.expense_analyst()
            )
        tasks.append(analysis_task)
        
        # Always end with report generation
        report_task = Task(
            description="Generate a comprehensive report based on the analysis",
            expected_output="Professional report with findings",
            agent=finbotics.report_generator(),
            context=[analysis_task]
        )
        tasks.append(report_task)
        
        # Create and run crew
        crew = Crew(
            agents=[
                finbotics.query_classifier(),
                finbotics.expense_analyst(),
                finbotics.report_generator()
            ],
            tasks=tasks,
            process="sequential",
            verbose=True
        )
        
        result = crew.kickoff()
        print(f"\nResult: {result}")

if __name__ == "__main__":
    print("Test 1: Simple Report Generation")
    print("="*60)
    test_simple_report_generation()
    
    print("\n\nTest 2: Complete End-to-End Flow")
    print("="*60)
    test_complete_expense_flow()
    
    print("\n\nTest 3: Multi-Agent Coordination")
    print("="*60)
    test_multi_agent_coordination()