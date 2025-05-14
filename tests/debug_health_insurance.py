# tests/debug_health_insurance.py
from src.finbotics.db.sqlite_setup import SQLiteSetup
import pandas as pd

def debug_health_insurance():
    """Debug health insurance queries"""
    db = SQLiteSetup()
    db.connect()
    
    print("=== Debugging Health Insurance Query ===\n")
    
    # 1. Check all unique descriptions in general_ledger
    print("1. Unique descriptions containing 'health' or 'insurance':")
    query = """
    SELECT DISTINCT description, COUNT(*) as count
    FROM general_ledger
    WHERE LOWER(description) LIKE '%health%' 
       OR LOWER(description) LIKE '%insurance%'
    GROUP BY description
    ORDER BY count DESC
    """
    results = db.execute_query(query)
    for r in results:
        print(f"  - {r['description']}: {r['count']} occurrences")
    
    # 2. Check all February 2024 transactions
    print("\n2. All February 2024 expenses:")
    query = """
    SELECT date, description, vendor, credit
    FROM general_ledger
    WHERE date >= '2024-02-01' AND date <= '2024-02-29'
      AND credit > 0
    ORDER BY credit DESC
    LIMIT 20
    """
    results = db.execute_query(query)
    for r in results:
        print(f"  {r['date']} - {r['description']} (Vendor: {r['vendor']}): ${r['credit']}")
    
    # 3. Search more broadly for insurance
    print("\n3. Broader insurance search:")
    query = """
    SELECT date, description, vendor, credit
    FROM general_ledger
    WHERE (LOWER(description) LIKE '%health%' 
           OR LOWER(description) LIKE '%insurance%'
           OR LOWER(vendor) LIKE '%health%'
           OR LOWER(vendor) LIKE '%insurance%'
           OR LOWER(description) LIKE '%benefit%')
      AND credit > 0
    LIMIT 10
    """
    results = db.execute_query(query)
    for r in results:
        print(f"  {r['date']} - {r['description']} (Vendor: {r['vendor']}): ${r['credit']}")
    
    # 4. Check the actual SQL being generated
    from src.finbotics.tools.nl_to_sql_tool import NaturalLanguageToSQLTool
    nl_to_sql = NaturalLanguageToSQLTool()
    
    test_query = "How much money did I spend on Health Insurance in February?"
    sql = nl_to_sql._run(test_query)
    print(f"\n4. Generated SQL for query:")
    print(f"   Query: {test_query}")
    print(f"   SQL: {sql}")
    
    # 5. Execute the generated SQL
    print(f"\n5. Results from generated SQL:")
    try:
        results = db.execute_query(sql)
        print(f"   Results: {results}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 6. Check for similar variations
    print("\n6. Checking different variations:")
    variations = [
        "SELECT SUM(credit) as total FROM general_ledger WHERE LOWER(description) LIKE '%health insurance%'",
        "SELECT SUM(credit) as total FROM general_ledger WHERE LOWER(vendor) LIKE '%health%'",
        "SELECT SUM(credit) as total FROM general_ledger WHERE LOWER(description) LIKE '%health%' AND date >= '2024-02-01' AND date <= '2024-02-29'",
    ]
    
    for sql in variations:
        try:
            results = db.execute_query(sql)
            print(f"   {sql}")
            print(f"   Result: {results}")
        except Exception as e:
            print(f"   Error: {e}")
    
    db.close()

if __name__ == "__main__":
    debug_health_insurance()