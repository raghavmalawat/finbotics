# tests/test_flexible_email_rag.py
from src.finbotics.tools.email_rag_tool import EmailRAGTool
from src.finbotics.query_processor import QueryProcessor
from pathlib import Path

def create_diverse_test_emails():
    """Create a variety of test emails for comprehensive testing"""
    email_dir = Path("data/emails")
    email_dir.mkdir(parents=True, exist_ok=True)
    
    test_emails = {
        "pilot_invoice_discussion.txt": """Subject: Re: January Invoice Issues
Date: February 15, 2024
From: jesstess@pilot.com
To: sarah@yourcompany.com

Hi Sarah,

Regarding the January invoice we discussed, I've made the following adjustments:
- Removed the duplicate $500 charge for tax preparation
- Applied the discount we agreed upon (10% off monthly services)
- New total: $2,250 (was $2,750)

Also, I noticed the Sevenn invoices in your books have some discrepancies. 
Two invoices appear to be duplicates - both for $5,000 dated January 15th.
Should we mark one as void?

Let me know if you need anything else.

Best,
Jessica
Pilot Bookkeeping""",

        "team_expense_discussion.txt": """Subject: Q1 Expense Review - Action Items
Date: March 10, 2024
From: cfo@yourcompany.com
To: finance-team@yourcompany.com

Team,

Following our Q1 expense review, here are the key findings:

1. Software costs up 25% due to new AI tools (OpenAI, Claude)
2. Travel expenses down 40% (remote-first policy working)
3. Vendor consolidation saved $15K/month
4. Health insurance premiums increased by $2K/month

Action items:
- Sarah: Negotiate with OpenAI for volume discount
- Mike: Review all software subscriptions for redundancy
- Jessica (Pilot): Prepare detailed vendor analysis

Our burn rate is currently $95K/month. With $1.2M in the bank, 
we have roughly 12-13 months runway.

Best,
Jane (CFO)""",

        "vendor_payment_update.txt": """Subject: Payment Status Update - Multiple Vendors
Date: March 5, 2024
From: ap@yourcompany.com
To: finance@yourcompany.com

Hi team,

Quick update on vendor payments:

PAID:
- OpenAI: $1,200 (February usage)
- AWS: $3,500 (February cloud services)
- Slack: $450 (Monthly subscription)

PENDING:
- Sevenn: $7,500 (On hold - invoice disputes)
- Deel: $12,000 (Processing - payroll for contractors)

ISSUES:
- Health insurance payment failed - wrong account number
- Google Workspace showing past due ($300)

Please update your records accordingly.

Thanks,
AP Team""",

        "budget_planning.txt": """Subject: 2024 Budget Planning - Final Numbers
Date: January 5, 2024
From: jesstess@pilot.com
To: leadership@yourcompany.com

Hi Leadership Team,

Here's our finalized 2024 budget based on our discussions:

Revenue Projections: $2.4M
- Q1: $500K
- Q2: $550K
- Q3: $600K
- Q4: $750K

Major Expense Categories:
- Payroll: $1.2M (50%)
- Software/Tools: $360K (15%)
- Office/Admin: $240K (10%)
- Marketing: $180K (7.5%)
- Other: $420K (17.5%)

Key Assumptions:
- 20% revenue growth YoY
- No additional hires until Q3
- Software costs stable after Q1 optimizations

Runway with current burn: 15 months

Let me know if you need any adjustments.

Jessica
Pilot Bookkeeping""",

        "customer_complaint.txt": """Subject: Urgent: Service Issues
Date: February 28, 2024
From: client@bigcorp.com
To: support@yourcompany.com

Your team,

We've experienced multiple issues this month:
1. API downtime on Feb 15-16 (lost $10K in revenue)
2. Incorrect billing - charged twice for Enterprise plan
3. Support response time over 48 hours

This is unacceptable for an Enterprise customer paying $5K/month.
We need immediate resolution or will consider switching providers.

John Smith
BigCorp CTO"""
    }
    
    # Create the email files
    for filename, content in test_emails.items():
        file_path = email_dir / filename
        with open(file_path, 'w') as f:
            f.write(content)
    
    return len(test_emails)

def test_flexible_email_queries():
    """Test various natural language queries about emails"""
    print("=== Flexible Email RAG Tests ===\n")
    
    # Create test emails
    num_created = create_diverse_test_emails()
    print(f"Created {num_created} test email files\n")
    
    # Initialize tools
    processor = QueryProcessor()
    email_tool = EmailRAGTool()
    
    # Test various natural language queries
    test_queries = [
        # Sender-based queries
        "latest 5 messages from jesstess@pilot.com",
        "what did jessica from pilot say about our budget?",
        "show me all emails from pilot",
        
        # Topic-based queries
        "find emails about invoice issues",
        "what happened with the Sevenn invoices?",
        "any discussions about software costs?",
        "emails mentioning OpenAI",
        
        # Time-based queries
        "emails from February 2024",
        "latest expense discussions",
        "most recent vendor payment updates",
        
        # Complex queries
        "how much runway do we have according to recent emails?",
        "what are our biggest expense categories?",
        "find complaints from customers",
        "summary of financial discussions with pilot",
        
        # Aggregation queries
        "how many emails mention invoice problems?",
        "count of emails from pilot.com",
        
        # Specific information queries
        "what was the health insurance payment issue?",
        "which vendors have pending payments?",
        "what discounts did we get from pilot?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        print("-" * 60)
        
        # Test direct tool
        result = email_tool._run(query=query)
        print(result[:500] + "..." if len(result) > 500 else result)
        
        print("\n" + "="*80)

def test_email_understanding():
    """Test the AI's understanding of email context"""
    print("\n\n=== Email Understanding Tests ===\n")
    
    processor = QueryProcessor()
    
    # Queries that require understanding context
    understanding_queries = [
        "What financial issues need immediate attention?",
        "Summarize all vendor payment problems",
        "What cost optimization opportunities were mentioned?",
        "List all action items from recent emails",
        "What are the main concerns raised by Jessica from Pilot?",
        "Find any mentions of duplicate charges or billing errors",
    ]
    
    for query in understanding_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        result, sources, found = processor.process_query(query)
        
        print(f"Data found: {found}")
        print(f"Sources: {sources}")
        print("\nResult:")
        print(result[:600] + "..." if len(result) > 600 else result)
        print("="*70)

def test_specific_rag_capabilities():
    """Test specific RAG capabilities"""
    print("\n\n=== Specific RAG Capabilities ===\n")
    
    email_tool = EmailRAGTool()
    
    # Test different query types
    test_cases = [
        {
            "query": "latest 3 messages from jesstess@pilot.com",
            "expected": "Should return chronological list of 3 most recent emails"
        },
        {
            "query": "emails about runway calculations",
            "expected": "Should find emails mentioning runway/burn rate"
        },
        {
            "query": "summarize vendor payment status",
            "expected": "Should provide summary of paid/pending/issue vendors"
        },
        {
            "query": "what's our burn rate?",
            "expected": "Should extract burn rate from relevant emails"
        }
    ]
    
    for test in test_cases:
        print(f"\nTest: {test['query']}")
        print(f"Expected: {test['expected']}")
        print("-" * 40)
        
        result = email_tool._run(query=test['query'])
        print(result[:400] + "..." if len(result) > 400 else result)
        print("="*60)

if __name__ == "__main__":
    test_flexible_email_queries()
    test_email_understanding()
    test_specific_rag_capabilities()