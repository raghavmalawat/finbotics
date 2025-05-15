# tests/test_complete_email_flow.py
import os
from pathlib import Path
from src.finbotics.query_processor import QueryProcessor
from src.finbotics.tools.email_search_tool import EmailSearchTool
from src.finbotics.analyzers.query_analyzer import QueryAnalyzer

def setup_test_emails():
    """Create test email files if they don't exist"""
    email_dir = Path("data/emails")
    email_dir.mkdir(parents=True, exist_ok=True)
    
    test_emails = {
        "email_feb_sevenn_issue.txt": """Subject: Re: Sevenn Invoice Issues
Date: February 15, 2024

Hi team,

We've been having ongoing issues with the Sevenn invoices. The main problems are:

1. Duplicate charges on invoice #INV-2024-001 for $5,000
2. Missing itemization for development services 
3. Tax calculations appear to be incorrect

I've reached out to their billing department but haven't received a response yet. 
The payment for January ($12,500) is on hold until we resolve these discrepancies.

Please escalate this with our account manager at Sevenn.

Best,
Sarah Finance
CFO""",
        
        "email_mar_sevenn_resolved.txt": """Subject: Update: Sevenn Invoice Issues - RESOLVED
Date: March 3, 2024

Team,

Good news - the Sevenn invoice issues have been resolved:

1. They've issued a credit for the duplicate $5,000 charge
2. Provided detailed itemization for all services
3. Corrected the tax calculations

New invoice total is $7,500 (down from $12,500). We've processed the payment 
and will apply the credit to next month's invoice.

Thanks for your patience with this.

Sarah Finance
CFO""",
        
        "email_openai_usage.txt": """Subject: OpenAI API Usage Update
Date: February 28, 2024

Hi all,

Quick update on our OpenAI API usage for February:

- Total API calls: 1.2M
- Estimated cost: $1,200
- Main usage: Customer service chatbot (70%), Internal tools (30%)

We're still within budget but usage is trending up. I recommend we review 
our token optimization strategy next week.

Best,
John Tech
CTO"""
    }
    
    # Create test email files
    created_files = []
    for filename, content in test_emails.items():
        file_path = email_dir / filename
        if not file_path.exists():
            with open(file_path, 'w') as f:
                f.write(content)
            created_files.append(filename)
    
    return created_files

def test_complete_flow():
    """Test the complete email search flow"""
    
    # Setup test emails
    created_files = setup_test_emails()
    if created_files:
        print(f"Created test email files: {created_files}")
    
    # Initialize components
    processor = QueryProcessor()
    email_tool = EmailSearchTool()
    analyzer = QueryAnalyzer()
    
    # Test queries
    test_cases = [
        {
            "query": "What happened to Sevenn invoices?",
            "expected_type": "email_communication",
            "should_find_email": True,
            "keywords": ["invoice issues", "duplicate charges", "resolved"]
        },
        {
            "query": "How much did I spend on OpenAI in February?",
            "expected_type": "expense_analysis", 
            "should_find_email": False,
            "keywords": ["spending", "total"]
        },
        {
            "query": "Find email about OpenAI usage",
            "expected_type": "email_communication",
            "should_find_email": True,
            "keywords": ["API usage", "estimated cost", "1,200"]
        },
        {
            "query": "What's the status of Sevenn payments and total amount?",
            "expected_type": "hybrid_financial_email",
            "should_find_email": True,
            "keywords": ["payment", "invoice", "resolved"]
        }
    ]
    
    print("=== Complete Email Flow Test ===\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"Test Case {i}: {test_case['query']}")
        print("-" * 60)
        
        # Analyze query
        analysis = analyzer.analyze_query(test_case['query'])
        print(f"Query Type: {analysis['query_type']}")
        print(f"Requires Email: {analysis['requires_email_search']}")
        
        # Process query
        result, sources, data_found = processor.process_query(test_case['query'])
        
        print(f"\nData Found: {data_found}")
        print(f"Sources: {sources}")
        
        # Check if email was searched when expected
        email_searched = any("email" in source.lower() for source in sources)
        print(f"Email Searched: {email_searched} (Expected: {test_case['should_find_email']})")
        
        # Check for expected keywords in result
        found_keywords = []
        for keyword in test_case['keywords']:
            if keyword.lower() in result.lower():
                found_keywords.append(keyword)
        
        print(f"Found Keywords: {found_keywords}")
        print(f"\nResult Preview:")
        print(result[:500] + "..." if len(result) > 500 else result)
        print("\n" + "="*60 + "\n")
    
    # Test direct email search
    print("Direct Email Search Tests:")
    print("-" * 60)
    
    search_terms = ["Sevenn", "invoice", "OpenAI", "payment"]
    for term in search_terms:
        result = email_tool._run(term, email_directory="data/emails")
        print(f"\nSearch: '{term}'")
        print(f"Found: {'Yes' if 'No matches found' not in result else 'No'}")
        if 'No matches found' not in result:
            print(f"Preview: {result[:200]}...")

if __name__ == "__main__":
    test_complete_flow()