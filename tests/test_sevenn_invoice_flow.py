# tests/test_sevenn_invoice_flow.py
from src.finbotics.query_processor import QueryProcessor
from src.finbotics.tools.email_search_tool import EmailSearchTool
from pathlib import Path

def setup_sevenn_email():
    """Create a realistic Sevenn invoice email"""
    email_dir = Path("data/emails")
    email_dir.mkdir(parents=True, exist_ok=True)
    
    email_content = """Subject: Update on Sevenn Invoice Issues
Date: March 15, 2024
From: sarah@yourcompany.com
To: finance-team@yourcompany.com

Hi team,

I wanted to provide an update on the Sevenn invoice situation we've been dealing with.

Background:
- Original invoice: $12,500 for Q1 development services
- Issue: Duplicate charges and incorrect tax calculations
- Status: RESOLVED as of March 10th

Resolution:
1. Sevenn acknowledged the duplicate billing error ($5,000)
2. They issued a credit note for the duplicate amount
3. Tax calculations have been corrected (saved us $375)
4. Final invoice amount: $7,125 (down from $12,500)

Next Steps:
- We've processed the corrected payment
- The credit will be applied to next month's invoice
- Our account manager at Sevenn (tim@sevenn.co) confirmed all future invoices will be reviewed before sending

Please update your records accordingly. Let me know if you need any documentation.

Best,
Sarah
CFO"""
    
    # Also create an email with encoding issues
    encoded_email = """Subject: Re: Sevenn Invoice - Urgent
Date: February 28, 2024

>>> Are these two invoices to tim@sevenn.co a) real invoices and b) still
>>> intended to be collected upon?

Yes, these are real invoices but we=E2=80=99ve put them on hold due to issues:

1. Duplicate charge of $5,000 on INV-2024-001
2. Missing itemization for dev services
3. Tax calc appears incorrect (showing 15% instead of 10%)

We=E2=80=99ve reached out to their billing dept but haven=E2=80=99t received response.
The payment for January ($12,500) is on hold until we resolve these discrepancies.

<img src=3D"cid:invoice_screenshot" alt=3D"invoice.png">

Sarah"""
    
    # Save emails
    (email_dir / "sevenn_invoice_update.txt").write_text(email_content)
    (email_dir / "sevenn_invoice_urgent.txt").write_text(encoded_email)
    
    return email_dir

def test_sevenn_invoice_search():
    """Test searching for Sevenn invoice information"""
    print("=== Sevenn Invoice Search Test ===\n")
    
    # Setup test emails
    email_dir = setup_sevenn_email()
    print(f"Created test emails in: {email_dir}")
    
    # Initialize tools
    processor = QueryProcessor()
    email_tool = EmailSearchTool()
    
    # Test direct email search
    print("\n1. Direct Email Search Test")
    print("-" * 40)
    search_result = email_tool._run("Sevenn invoice", str(email_dir))
    print(search_result)
    
    # Test queries through processor
    queries = [
        "What happened to Sevenn invoices?",
        "What's the status of the Sevenn invoice issues?",
        "How much do we owe Sevenn?",
        "Find email about Sevenn billing problems"
    ]
    
    print("\n\n2. Query Processor Tests")
    print("=" * 60)
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        result, sources, data_found = processor.process_query(query)
        
        print(f"Sources: {sources}")
        print(f"Data Found: {data_found}")
        print("\nResult:")
        print(result)
        print("\n" + "=" * 60)
    
    # Test that encoding is properly handled
    print("\n\n3. Encoding Test")
    print("-" * 40)
    encoded_search = email_tool._run("haven't received response", str(email_dir))
    print("Search for encoded text:")
    print(encoded_search)
    
    # Verify the output is clean
    bad_patterns = ['=E2=80=99', '=3D', 'cid:', '[image:', '>>>']
    issues_found = []
    for pattern in bad_patterns:
        if pattern in encoded_search:
            issues_found.append(pattern)
    
    if issues_found:
        print(f"\n⚠️  Found encoding issues: {issues_found}")
    else:
        print("\n✅ Output is clean - no encoding issues found!")

def test_formatting_comparison():
    """Compare old vs new formatting"""
    print("\n\n=== Formatting Comparison ===\n")
    
    # Sample of the old problematic output
    old_output = """Line 89: >>> [image: image.png] >>> >>> Are these two invoices to tim@sevenn.co a) real invoices and b) still >>> intended to be collected upon? >>> Line 138: or categorization, only one vendor was reclassified under professional deve= lopment.</p> <p>As for the invoices to Sevenn, these were real invoices, but they were n= ot paid. We=E2=80=99ve deactivated their paid subscription for now"""
    
    print("OLD OUTPUT (problematic):")
    print(old_output[:200] + "...")
    
    print("\n\nNEW OUTPUT (clean):")
    email_tool = EmailSearchTool()
    cleaned = email_tool._clean_email_content(old_output)
    print(cleaned[:200] + "...")
    
    print("\n\nKey improvements:")
    print("- Removed line numbers and >>> markers")
    print("- Decoded HTML entities (=E2=80=99 → ')")
    print("- Removed image references and HTML tags")
    print("- Fixed quoted-printable encoding (= at line ends)")
    print("- Cleaned up spacing and formatting")

if __name__ == "__main__":
    test_sevenn_invoice_search()
    test_formatting_comparison()