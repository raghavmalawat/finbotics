# tests/debug_health_insurance_discrepancy.py
from src.finbotics.db.sqlite_setup import SQLiteSetup
from src.finbotics.tools.nl_to_sql_tool import NaturalLanguageToSQLTool
from src.finbotics.tools.financial_search_tool import FinancialSearchTool
from datetime import datetime
import pandas as pd
import json

def debug_health_insurance_discrepancy():
    """Debug the health insurance discrepancy"""
    db = SQLiteSetup()
    db.connect()
    
    print("=== Debugging Health Insurance Discrepancy ===\n")
    
    # 1. First, let's check what the NL to SQL tool generates
    nl_to_sql = NaturalLanguageToSQLTool()
    query = "How much money did I spend on Health Insurance in February?"
    generated_sql = nl_to_sql._run(query)
    
    print(f"1. User Query: {query}")
    print(f"   Generated SQL: {generated_sql}\n")
    
    # 2. Execute the generated SQL and see what it returns
    print("2. Executing generated SQL:")
    try:
        results = db.execute_query(generated_sql)
        print(f"   Raw results: {results}")
        if results and 'total_spent' in results[0]:
            print(f"   Bot's answer: ${results[0]['total_spent']:,.2f}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # 3. Let's manually check ALL health insurance transactions
    print("\n3. Manual check - ALL Health Insurance transactions:")
    manual_sql = """
    SELECT date, description, vendor, credit
    FROM general_ledger
    WHERE (LOWER(description) LIKE '%health insurance%' 
           OR LOWER(description) LIKE '%health%benefit%'
           OR LOWER(vendor) LIKE '%health%')
      AND credit > 0
    ORDER BY date
    """
    all_transactions = db.execute_query(manual_sql)
    
    total_all_time = 0
    for trans in all_transactions:
        print(f"   {trans['date']} - {trans['description']} - ${trans['credit']:,.2f}")
        total_all_time += trans['credit']
    
    print(f"\n   Total (all time): ${total_all_time:,.2f}")
    
    # 4. Check February 2025 specifically
    print("\n4. February 2025 transactions only:")
    feb_2025_sql = """
    SELECT date, description, vendor, credit
    FROM general_ledger
    WHERE (LOWER(description) LIKE '%health insurance%' 
           OR LOWER(description) LIKE '%health%benefit%'
           OR LOWER(vendor) LIKE '%health%')
      AND date >= '2025-02-01' 
      AND date <= '2025-02-28'
      AND credit > 0
    ORDER BY date
    """
    feb_transactions = db.execute_query(feb_2025_sql)
    
    feb_total = 0
    for trans in feb_transactions:
        print(f"   {trans['date']} - {trans['description']} - ${trans['credit']:,.2f}")
        feb_total += trans['credit']
    
    print(f"\n   February 2025 total: ${feb_total:,.2f}")
    
    # 5. Check if the bot is looking at the wrong time period
    print("\n5. Checking different time periods:")
    periods = [
        ('2024-02', '2024-02-01', '2024-02-29'),
        ('2025-01', '2025-01-01', '2025-01-31'),
        ('2025-02', '2025-02-01', '2025-02-28'),
    ]
    
    for period_name, start_date, end_date in periods:
        period_sql = f"""
        SELECT SUM(credit) as total
        FROM general_ledger
        WHERE (LOWER(description) LIKE '%health insurance%' 
               OR LOWER(description) LIKE '%health%benefit%')
          AND date >= '{start_date}' 
          AND date <= '{end_date}'
          AND credit > 0
        """
        result = db.execute_query(period_sql)
        total = result[0]['total'] if result and result[0]['total'] else 0
        print(f"   {period_name}: ${total:,.2f}")
    
    # 6. Check the exact SQL conditions the bot is using
    print("\n6. Testing different SQL conditions:")
    conditions = [
        ("Just 'health insurance'", "LOWER(description) LIKE '%health insurance%'"),
        ("Just 'health'", "LOWER(description) LIKE '%health%'"),
        ("Vendor based", "LOWER(vendor) LIKE '%health%'"),
        ("Combined", "(LOWER(description) LIKE '%health%' OR LOWER(vendor) LIKE '%health%')"),
    ]
    
    for desc, condition in conditions:
        test_sql = f"""
        SELECT SUM(credit) as total
        FROM general_ledger
        WHERE {condition}
          AND credit > 0
        """
        result = db.execute_query(test_sql)
        total = result[0]['total'] if result and result[0]['total'] else 0
        print(f"   {desc}: ${total:,.2f}")
    
    # 7. Let's trace through the entire search flow
    print("\n7. Full search flow trace:")
    search_tool = FinancialSearchTool()
    search_result = search_tool._run(query)
    
    print("   Search tool result:")
    try:
        result_data = json.loads(search_result)
        print(f"   SQL generated: {result_data.get('sql_generated', 'N/A')}")
        print(f"   Results: {result_data.get('results', 'N/A')}")
    except:
        print(f"   Raw result: {search_result}")
    
    db.close()

if __name__ == "__main__":
    debug_health_insurance_discrepancy()