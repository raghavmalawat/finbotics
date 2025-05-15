# tests/test_final_sevenn_email.py
from src.finbotics.tools.email_rag_tool import EmailRAGTool
from src.finbotics.query_processor import QueryProcessor
from pathlib import Path

def test_sevenn_email_extraction():
    """Final test for Sevenn email extraction"""
    
    print("=== Final Sevenn Email Test ===\n")
    
    # Make sure we have the email file
    email_file = Path("data/emails/acmeai_email_feb.txt")
    if not email_file.exists():
        print(f"Error: Email file not found at {email_file}")
        return
    
    # Initialize tools
    email_tool = EmailRAGTool()
    processor = QueryProcessor()
    
    # Test 1: Direct tool test
    print("1. Direct Email Tool Test")
    print("-" * 50)
    
    query = "what happened to the sevenn invoices"
    result = email_tool._run(query=query, email_directory="data/emails")
    print(result)
    
    # Test 2: Look for specific content
    print("\n\n2. Specific Content Extraction")
    print("-" * 50)
    
    with open(email_file, 'r', encoding='utf-8', errors='ignore') as f:
        raw_content = f.read()
    
    # Parse the email
    email_data = email_tool._parse_email(raw_content, email_file.name)
    
    # Extract Sevenn-specific content
    sevenn_excerpt = email_tool._extract_sevenn_context(raw_content)
    print("Sevenn-specific excerpt:")
    print(sevenn_excerpt)
    
    # Test 3: Full query processor
    print("\n\n3. Full Query Processor Test")
    print("-" * 50)
    
    result, sources, data_found = processor.process_query(query)
    print(f"Data found: {data_found}")
    print(f"Sources: {sources}")
    print("\nResult:")
    print(result)
    
    # Test 4: Verify we found the key information
    print("\n\n4. Verification")
    print("-" * 50)
    
    key_phrases = [
        "were real invoices",
        "were not paid",
        "deactivated their paid subscription",
        "marked their subscription as cancelled",
        "tim@sevenn.co"
    ]
    
    found_phrases = []
    missing_phrases = []
    
    for phrase in key_phrases:
        if phrase.lower() in result.lower() or phrase.lower() in sevenn_excerpt.lower():
            found_phrases.append(phrase)
        else:
            missing_phrases.append(phrase)
    
    print(f"Found key phrases: {found_phrases}")
    print(f"Missing phrases: {missing_phrases}")
    
    if len(found_phrases) >= 3:
        print("\n✅ SUCCESS: Found the important information about Sevenn invoices!")
    else:
        print("\n⚠️  WARNING: Some key information might be missing")

def debug_mime_parsing():
    """Debug MIME email parsing"""
    print("\n\n=== MIME Email Parsing Debug ===\n")
    
    email_file = Path("data/emails/acmeai_email_feb.txt")
    with open(email_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    email_tool = EmailRAGTool()
    
    # Test MIME parsing
    text_content = email_tool._parse_mime_email(content)
    print("Extracted text content (first 500 chars):")
    print(text_content[:500])
    
    # Test quoted-printable decoding
    decoded = email_tool._decode_quoted_printable(text_content)
    print("\n\nDecoded content (first 500 chars):")
    print(decoded[:500])
    
    # Look for Sevenn in decoded content
    if 'sevenn' in decoded.lower():
        print("\n✅ Found 'sevenn' in decoded content")
        # Find the context
        lines = decoded.split('\n')
        for i, line in enumerate(lines):
            if 'sevenn' in line.lower():
                start = max(0, i-2)
                end = min(len(lines), i+3)
                print(f"\nContext around line {i}:")
                print('\n'.join(lines[start:end]))

if __name__ == "__main__":
    test_sevenn_email_extraction()
    debug_mime_parsing()