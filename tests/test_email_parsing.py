# tests/test_email_parsing.py
from src.finbotics.tools.email_search_tool import EmailSearchTool
from pathlib import Path

def create_test_email_with_encoding():
    """Create a test email with encoding issues like the one shown"""
    email_dir = Path("data/emails")
    email_dir.mkdir(parents=True, exist_ok=True)
    
    encoded_content = """Subject: Re: Sevenn Invoice Status
Date: February 15, 2024

Line 89:
>>> [image: image.png]
>>>
>>> Are these two invoices to tim@sevenn.co a) real invoices and b) still
>>> intended to be collected upon?
>>>
Line 138:
or categorization, only one vendor was reclassified under professional deve=
lopment.</p>
<p>As for the invoices to Sevenn, these were real invoices, but they were n=
ot paid. We=E2=80=99ve deactivated their paid subscription for now, and mar=
ked their subscription as cancelled. Let us know if there=E2=80=99s anythin=

Line 184:
=A0I wanted to flag the status of some invoices in Stripe:</p><p></p><img s=
rc=3D"cid:ii_m86y9ac40" alt=3D"image.png" width=3D"520" height=3D"144"><br>
<br>Are these two invoices to <a href=3D"mailto:tim@sevenn.co" target=
=3D"_blank">tim@sevenn.co</a> a) real invoices and b) still intended to be =
collected upon?</div><div><br></div><div>If they are not real invoices, you=

Additional context:
The Sevenn invoices totaled $12,500 for development services. We've put the payment on hold pending resolution of the duplicate charges.

Sarah
CFO"""
    
    test_file = email_dir / "test_sevenn_encoded.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(encoded_content)
    
    return test_file

def test_email_cleaning():
    """Test the email cleaning functionality"""
    print("=== Email Parsing Test ===\n")
    
    # Create test email
    test_file = create_test_email_with_encoding()
    print(f"Created test file: {test_file}")
    
    # Test the search tool
    email_tool = EmailSearchTool()
    
    # Test search for Sevenn
    result = email_tool._run("Sevenn", email_directory="data/emails")
    
    print("\nSearch Result:")
    print("-" * 50)
    print(result)
    print("-" * 50)
    
    # Test specific encoding issues
    print("\n\nTesting encoding fixes:")
    
    test_strings = [
        ("We=E2=80=99ve deactivated", "We've deactivated"),
        ("href=3D\"mailto:tim@sevenn.co\"", "tim@sevenn.co"),
        ("there=E2=80=99s anythin=", "there's anythin"),
        ("[image: image.png]", "[should be removed]"),
        ("Line 89:", "[should be removed]"),
    ]
    
    for encoded, expected in test_strings:
        cleaned = email_tool._clean_email_content(encoded)
        print(f"\nOriginal: {encoded}")
        print(f"Cleaned:  {cleaned}")
        print(f"Expected: {expected}")
        print(f"Success:  {'✓' if expected in cleaned or cleaned == '' else '✗'}")

def test_sevenn_query():
    """Test the full Sevenn query flow"""
    print("\n\n=== Full Sevenn Query Test ===\n")
    
    from src.finbotics.query_processor import QueryProcessor
    
    processor = QueryProcessor()
    queries = [
        "What happened to Sevenn invoices?",
        "Find Sevenn invoice status",
        "Email about Sevenn payments"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        result, sources, data_found = processor.process_query(query)
        
        print(f"Sources: {sources}")
        print(f"Data found: {data_found}")
        print("\nResult:")
        print(result[:500] + "..." if len(result) > 500 else result)
        print("=" * 60)

if __name__ == "__main__":
    test_email_cleaning()
    test_sevenn_query()