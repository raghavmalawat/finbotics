# tests/debug_top_vendors.py
from src.finbotics.tools.nl_to_sql_tool import NaturalLanguageToSQLTool
from src.finbotics.db.sqlite_setup import SQLiteSetup
import re

def debug_top_vendors():
    """Debug the top vendors query issue"""
    
    print("=== Debugging Top Vendors Query ===\n")
    
    # 1. Test the regex pattern
    test_queries = [
        "show me the top 5 vendors by spending",
        "show me the top 10 vendors by spending",
        "show me the top 15 vendors by spending",
        "show me top 3 vendors",
        "what are my top vendors"
    ]
    
    print("1. Testing number extraction:")
    for query in test_queries:
        num_match = re.search(r'top\s+(\d+)', query.lower())
        extracted = num_match.group(1) if num_match else 'default 5'
        print(f"   Query: '{query}' -> Extracted: {extracted}")
    
    # 2. Test SQL generation
    nl_to_sql = NaturalLanguageToSQLTool()
    
    print("\n2. Testing SQL generation:")
    for query in test_queries:
        sql = nl_to_sql._run(query)
        print(f"   Query: '{query}'")
        print(f"   SQL: {sql}\n")
    
    # 3. Check what's in the expense_summary table
    db = SQLiteSetup()
    db.connect()
    
    print("3. Checking expense_summary table:")
    
    # Count total vendors
    count_sql = "SELECT COUNT(*) as count FROM expense_summary"
    result = db.execute_query(count_sql)
    print(f"   Total vendors in table: {result[0]['count']}")
    
    # Check for TOTAL row
    total_check_sql = "SELECT * FROM expense_summary WHERE UPPER(vendor_name) = 'TOTAL'"
    total_rows = db.execute_query(total_check_sql)
    print(f"   TOTAL rows found: {len(total_rows)}")
    if total_rows:
        print(f"   TOTAL row: {total_rows[0]}")
    
    # Get top vendors without TOTAL
    print("\n4. Testing different queries:")
    
    queries = [
        ("With LIMIT 5", """
            SELECT vendor_name, total 
            FROM expense_summary 
            WHERE UPPER(vendor_name) != 'TOTAL' 
            ORDER BY total DESC 
            LIMIT 5
        """),
        ("With LIMIT 10", """
            SELECT vendor_name, total 
            FROM expense_summary 
            WHERE UPPER(vendor_name) != 'TOTAL' 
            ORDER BY total DESC 
            LIMIT 10
        """),
        ("With LIMIT 15", """
            SELECT vendor_name, total 
            FROM expense_summary 
            WHERE UPPER(vendor_name) != 'TOTAL' 
            ORDER BY total DESC 
            LIMIT 15
        """),
        ("Without LIMIT", """
            SELECT vendor_name, total 
            FROM expense_summary 
            WHERE UPPER(vendor_name) != 'TOTAL' 
            ORDER BY total DESC
        """),
    ]
    
    for desc, sql in queries:
        results = db.execute_query(sql.strip())
        print(f"\n   {desc}:")
        print(f"   Results count: {len(results)}")
        if results:
            for i, row in enumerate(results[:5], 1):  # Show first 5
                print(f"   {i}. {row['vendor_name']}: ${row['total']:,.2f}")
            if len(results) > 5:
                print(f"   ... and {len(results) - 5} more")
    
    # 5. Check the actual SQL being executed by the tool
    print("\n5. Full flow test:")
    query = "show me the top 15 vendors by spending"
    
    # Get the SQL from the tool
    generated_sql = nl_to_sql._run(query)
    print(f"   Query: {query}")
    print(f"   Generated SQL: {generated_sql}")
    
    # Execute it
    try:
        results = db.execute_query(generated_sql)
        print(f"   Results count: {len(results)}")
        for i, row in enumerate(results[:3], 1):
            print(f"   {i}. {row}")
    except Exception as e:
        print(f"   Error: {e}")
    
    db.close()

if __name__ == "__main__":
    debug_top_vendors()