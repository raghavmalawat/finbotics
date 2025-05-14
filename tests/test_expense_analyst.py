# test_expense_analyst.py
from src.finbotics.crew import Finbotics
from crewai import Crew, Task

def test_direct_expense_analysis():
    """Test direct expense analysis for a specific vendor"""
    
    crew_instance = Finbotics()
    
    # Create a simple task for direct expense analysis
    direct_expense_task = Task(
        description="""
        Analyze expenses for vendor: OpenAI
        Time period: February 2024
        
        Search through the general ledger to find all transactions.
        Provide total spending and transaction details.
        """,
        expected_output="""
        A detailed expense report containing:
        - Total spent with vendor
        - List of transactions
        - Any patterns observed
        """,
        agent=crew_instance.expense_analyst()
    )
    
    # Direct expense analysis
    crew = Crew(
        agents=[crew_instance.expense_analyst()],
        tasks=[direct_expense_task],
        process="sequential",
        verbose=True
    )
    
    result = crew.kickoff()
    print(f"\nExpense Analysis Result: {result}")

def test_classification_then_expense():
    """Test classification followed by expense analysis"""
    
    crew_instance = Finbotics()
    
    # Create tasks without template variables first
    classification_task = Task(
        description="""
        Analyze this financial query: "How much did I spend on OpenAI in February?"
        
        Identify:
        1. Query type (expense_analysis)
        2. Vendor mentioned (OpenAI)
        3. Time period (February)
        4. Required data sources
        """,
        expected_output="""
        Query classification:
        - query_type: expense_analysis
        - vendor: OpenAI
        - time_period: February
        - data_sources: general_ledger
        """,
        agent=crew_instance.query_classifier()
    )
    
    expense_task = Task(
        description="""
        Based on the classification results, analyze expenses for:
        - Vendor: OpenAI (extracted from classification)
        - Time period: February (extracted from classification)
        
        Find all transactions and provide total spending.
        """,
        expected_output="""
        Expense report with total spending and transaction details
        """,
        agent=crew_instance.expense_analyst(),
        context=[classification_task]  # This links the tasks
    )
    
    # Create crew with both tasks
    crew = Crew(
        agents=[
            crew_instance.query_classifier(),
            crew_instance.expense_analyst()
        ],
        tasks=[
            classification_task,
            expense_task
        ],
        process="sequential",
        verbose=True
    )
    
    result = crew.kickoff()
    print(f"\nFinal Result: {result}")

def test_simple_expense_query():
    """Test a simple expense query flow"""
    
    crew_instance = Finbotics()
    
    # Single task that combines classification and analysis
    combined_task = Task(
        description="""
        User query: "How much did I spend on OpenAI in February?"
        
        1. First, identify that this is an expense query for vendor "OpenAI" in "February"
        2. Then, search the general ledger for OpenAI transactions in February
        3. Calculate total spending and list all transactions
        """,
        expected_output="""
        Complete analysis including:
        - Query understanding (vendor: OpenAI, period: February)
        - Total amount spent
        - Transaction details
        - Summary of findings
        """,
        agent=crew_instance.expense_analyst()
    )
    
    crew = Crew(
        agents=[crew_instance.expense_analyst()],
        tasks=[combined_task],
        process="sequential",
        verbose=True
    )
    
    result = crew.kickoff()
    print(f"\nResult: {result}")

if __name__ == "__main__":
    print("Test 1: Direct Expense Analysis")
    print("="*50)
    test_direct_expense_analysis()
    
    print("\n\nTest 2: Classification then Expense")
    print("="*50)
    test_classification_then_expense()
    
    print("\n\nTest 3: Simple Combined Query")
    print("="*50)
    test_simple_expense_query()