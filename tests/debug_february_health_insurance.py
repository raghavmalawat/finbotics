# tests/debug_february_health_insurance.py
from src.finbotics.query_processor import QueryProcessor
from src.finbotics.tools.nl_to_sql_tool import NaturalLanguageToSQLTool
from src.finbotics.db.sqlite_setup import SQLiteSetup
import json

def debug_february_query():
    """Debug the specific February health insurance query"""
    
    print("=== Debugging February Health Insurance Query ===\n")
    
    # 1. Test the complete flow
    processor = QueryProcessor()
    query = "How much money did I spend on Health Insurance in February?"
    
    print(f"1. Processing query: {query}")
    result, sources, data_found = processor.process_query(query)
    
    print(f"\n   Result: {result}")
    print(f"   Sources: {sources}")
    print(f"   Data found: {data_found}")
    
    # 2. Check what SQL is generated
    nl_to_sql = NaturalLanguageToSQLTool()
    generated_sql = nl_to_sql._run(query)
    
    print(f"\n2. Generated SQL: {generated_sql}")
    
    # 3. Execute the SQL directly
    db = SQLiteSetup()
    db.connect()
    
    print("\n3. Direct SQL execution:")
    try:
        results = db.execute_query(generated_sql)
        print(f"   Results: {results}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 4. Try different variations
    print("\n4. Testing SQL variations:")
    
    variations = [
        # February 2025
        ("February 2025", """
            SELECT SUM(credit) as total_spent 
            FROM general_ledger 
            WHERE LOWER(description) LIKE '%health insurance%' 
            AND date >= '2025-02-01' AND date <= '2025-02-28' 
            AND credit > 0
        """),
        
        # February 2024 (in case year is wrong)
        ("February 2024", """
            SELECT SUM(credit) as total_spent 
            FROM general_ledger 
            WHERE LOWER(description) LIKE '%health insurance%' 
            AND date >= '2024-02-01' AND date <= '2024-02-29' 
            AND credit > 0
        """),
        
        # All time health insurance
        ("All time", """
            SELECT SUM(credit) as total_spent 
            FROM general_ledger 
            WHERE LOWER(description) LIKE '%health insurance%' 
            AND credit > 0
        """),
        
        # Broader health search
        ("Broader health search", """
            SELECT SUM(credit) as total_spent 
            FROM general_ledger 
            WHERE (LOWER(description) LIKE '%health%' 
                   OR LOWER(vendor) LIKE '%health%') 
            AND date >= '2025-02-01' AND date <= '2025-02-28' 
            AND credit > 0
        """),
    ]
    
    for desc, sql in variations:
        try:
            result = db.execute_query(sql.strip())
            total = result[0]['total_spent'] if result and result[0]['total_spent'] else 0
            print(f"   {desc}: ${total:,.2f}")
        except Exception as e:
            print(f"   {desc}: Error - {e}")
    
    # 5. Show actual February transactions
    print("\n5. Actual February health insurance transactions:")
    detail_sql = """
    SELECT date, description, vendor, credit
    FROM general_ledger
    WHERE LOWER(description) LIKE '%health insurance%'
    AND date >= '2025-02-01' AND date <= '2025-02-28'
    AND credit > 0
    ORDER BY date
    """
    
    transactions = db.execute_query(detail_sql)
    total = 0
    for trans in transactions:
        print(f"   {trans['date']} - {trans['description']} - ${trans['credit']:,.2f}")
        total += trans['credit']
    
    print(f"\n   Manual total: ${total:,.2f}")
    
    db.close()

if __name__ == "__main__":
    debug_february_query()