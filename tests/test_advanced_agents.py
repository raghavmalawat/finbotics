from src.finbotics.crew import Finbotics
from crewai import Crew, Task

def test_runway_calculation():
    """Test runway calculation flow"""
    
    finbotics = Finbotics()
    
    # Security check first
    security_task = Task(
        description="""
        Validate access for customer 'acme_ai' to access financial data.
        """,
        expected_output="Security validation result",
        agent=finbotics.security_guardian()
    )
    
    # Calculate burn rate
    burn_rate_task = Task(
        description="""
        Calculate the monthly burn rate based on the last 3 months of expenses.
        Analyze expense trends and identify major cost categories.
        """,
        expected_output="Monthly burn rate analysis",
        agent=finbotics.cash_flow_analyst()
    )
    
    # Calculate runway
    runway_task = Task(
        description="""
        Calculate the company's runway based on current cash position and burn rate.
        Use the balance sheet for cash position and the calculated burn rate.
        """,
        expected_output="Runway projection in months",
        agent=finbotics.cash_flow_analyst(),
        context=[burn_rate_task]
    )
    
    # Generate report
    report_task = Task(
        description="""
        Create a comprehensive runway report including burn rate analysis
        and runway projections with recommendations.
        """,
        expected_output="Professional runway report",
        agent=finbotics.report_generator(),
        context=[burn_rate_task, runway_task]
    )
    
    crew = Crew(
        agents=[
            finbotics.security_guardian(),
            finbotics.cash_flow_analyst(),
            finbotics.report_generator()
        ],
        tasks=[
            security_task,
            burn_rate_task,
            runway_task,
            report_task
        ],
        process="sequential",
        verbose=True
    )
    
    result = crew.kickoff()
    print("\n" + "="*60)
    print("RUNWAY ANALYSIS RESULT:")
    print("="*60)
    print(result)

def test_email_context_search():
    """Test email context search for vendor issues"""
    
    finbotics = Finbotics()
    
    queries = [
        "What happened with the Sevenn invoices?",
        "Any issues with OpenAI billing?",
        "Find all discussions about payment terms"
    ]
    
    for query in queries:
        print(f"\n\n{'='*60}")
        print(f"Email Query: {query}")
        print('='*60)
        
        # Extract search term from query
        if "Sevenn" in query:
            search_term = "Sevenn"
        elif "OpenAI" in query:
            search_term = "OpenAI"
        else:
            search_term = "payment terms"
        
        email_task = Task(
            description=f"""
            Search email correspondence for: {search_term}
            Use the email directory at: data/emails
            Find any discussions, issues, or decisions related to this topic.
            """,
            expected_output="Email context report with relevant excerpts",
            agent=finbotics.email_context_agent()
        )
        
        crew = Crew(
            agents=[finbotics.email_context_agent()],
            tasks=[email_task],
            process="sequential",
            verbose=True
        )
        
        result = crew.kickoff()
        print(f"\nEmail Search Result: {result}")

def test_integrated_vendor_analysis():
    """Test integrated analysis combining financial data and email context"""
    
    finbotics = Finbotics()
    
    vendor = "Sevenn"
    
    # Security validation
    security_task = Task(
        description="Validate access for customer 'acme_ai'",
        expected_output="Access validation",
        agent=finbotics.security_guardian()
    )
    
    # Financial analysis
    expense_task = Task(
        description=f"""
        Analyze all expenses for vendor: {vendor}
        Find total spending, transaction history, and patterns.
        """,
        expected_output="Vendor expense analysis",
        agent=finbotics.expense_analyst()
    )
    
    # Email context
    email_task = Task(
        description=f"""
        Search emails for any discussions about {vendor}.
        Find invoice issues, payment terms, or service problems.
        """,
        expected_output="Email context about vendor",
        agent=finbotics.email_context_agent()
    )
    
    # Combined report
    report_task = Task(
        description=f"""
        Create a comprehensive vendor analysis report for {vendor}.
        Combine financial data with email context to tell the complete story.
        """,
        expected_output="Complete vendor analysis report",
        agent=finbotics.report_generator(),
        context=[expense_task, email_task]
    )
    
    crew = Crew(
        agents=[
            finbotics.security_guardian(),
            finbotics.expense_analyst(),
            finbotics.email_context_agent(),
            finbotics.report_generator()
        ],
        tasks=[
            security_task,
            expense_task,
            email_task,
            report_task
        ],
        process="sequential",
        verbose=True
    )
    
    result = crew.kickoff()
    print("\n" + "="*60)
    print("INTEGRATED VENDOR ANALYSIS:")
    print("="*60)
    print(result)

def test_security_validation():
    """Test security validation for different scenarios"""
    
    finbotics = Finbotics()
    
    # Test authorized access
    auth_task = Task(
        description="""
        Validate access for customer 'acme_ai' to read financial data.
        """,
        expected_output="Access validation result",
        agent=finbotics.security_guardian()
    )
    
    # Test unauthorized access
    unauth_task = Task(
        description="""
        Validate access for customer 'competitor_corp' to read financial data.
        """,
        expected_output="Access denial result",
        agent=finbotics.security_guardian()
    )
    
    crew = Crew(
        agents=[finbotics.security_guardian()],
        tasks=[auth_task, unauth_task],
        process="sequential",
        verbose=True
    )
    
    result = crew.kickoff()
    print(f"\nSecurity Validation Results: {result}")

if __name__ == "__main__":
    print("Test 1: Runway Calculation")
    print("="*60)
    test_runway_calculation()
    
    print("\n\nTest 2: Email Context Search")
    print("="*60)
    test_email_context_search()
    
    print("\n\nTest 3: Integrated Vendor Analysis")
    print("="*60)
    test_integrated_vendor_analysis()
    
    print("\n\nTest 4: Security Validation")
    print("="*60)
    test_security_validation()