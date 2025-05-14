# tests/compare_csv_vs_db.py
import pandas as pd
from src.finbotics.db.sqlite_setup import SQLiteSetup
import re

def parse_amount(amount):
    """Parse amount string to float"""
    if pd.isna(amount):
        return 0.0
    
    # Convert to string and clean
    amount_str = str(amount).strip()
    
    # Remove currency symbols and commas
    amount_str = amount_str.replace('$', '').replace(',', '').strip()
    
    # Handle parentheses for negative values
    if amount_str.startswith('(') and amount_str.endswith(')'):
        amount_str = '-' + amount_str[1:-1].strip()
    
    try:
        return float(amount_str)
    except:
        return 0.0

def compare_csv_vs_db():
    """Compare CSV data with database for health insurance"""
    
    print("=== Comparing CSV vs Database ===\n")
    
    # 1. Read the CSV
    df = pd.read_csv('data/csv/general_ledger.csv')
    
    # Convert date column to datetime
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Convert Amount column to numeric
    df['Amount_Numeric'] = df['Amount'].apply(parse_amount)
    
    # 2. Filter for health insurance in CSV
    health_mask = df.apply(lambda row: any(
        'health' in str(val).lower() or 'insurance' in str(val).lower() 
        for val in row.values if pd.notna(val)
    ), axis=1)
    
    health_df = df[health_mask].copy()
    
    print(f"1. CSV Data - Health Insurance entries: {len(health_df)}")
    
    # Show sample of Amount values to understand format
    print("\n   Sample Amount values:")
    for idx, row in health_df.head().iterrows():
        print(f"     Original: '{row['Amount']}' -> Numeric: {row['Amount_Numeric']}")
    
    # Calculate total from CSV
    # Negative amounts are typically expenses
    csv_total = abs(health_df[health_df['Amount_Numeric'] < 0]['Amount_Numeric'].sum())
    print(f"\n   Total from CSV (all time, negative amounts): ${csv_total:,.2f}")
    
    # Also check positive amounts in case they represent expenses
    csv_total_positive = health_df[health_df['Amount_Numeric'] > 0]['Amount_Numeric'].sum()
    print(f"   Total from CSV (all time, positive amounts): ${csv_total_positive:,.2f}")
    
    # February 2025 only
    feb_2025_mask = (health_df['Date'].dt.year == 2025) & (health_df['Date'].dt.month == 2)
    feb_health_df = health_df[feb_2025_mask]
    
    if len(feb_health_df) > 0:
        feb_csv_total_negative = abs(feb_health_df[feb_health_df['Amount_Numeric'] < 0]['Amount_Numeric'].sum())
        feb_csv_total_positive = feb_health_df[feb_health_df['Amount_Numeric'] > 0]['Amount_Numeric'].sum()
        
        print(f"\n   February 2025 from CSV:")
        print(f"     Negative amounts: ${feb_csv_total_negative:,.2f}")
        print(f"     Positive amounts: ${feb_csv_total_positive:,.2f}")
        print(f"     Total transactions: {len(feb_health_df)}")
    else:
        print("\n   No February 2025 entries found in CSV")
    
    # 3. Compare with database
    db = SQLiteSetup()
    db.connect()
    
    print("\n2. Database Data:")
    
    # All time total
    all_time_sql = """
    SELECT SUM(credit) as total_credit, SUM(debit) as total_debit, COUNT(*) as count
    FROM general_ledger
    WHERE (LOWER(description) LIKE '%health%' 
           OR LOWER(vendor) LIKE '%health%'
           OR LOWER(description) LIKE '%insurance%'
           OR LOWER(vendor) LIKE '%insurance%')
    """
    result = db.execute_query(all_time_sql)
    if result:
        db_credit_total = result[0]['total_credit'] or 0
        db_debit_total = result[0]['total_debit'] or 0
        db_count = result[0]['count'] or 0
        print(f"   Total from DB (all time):")
        print(f"     Credit (expenses): ${db_credit_total:,.2f}")
        print(f"     Debit: ${db_debit_total:,.2f}")
        print(f"     Transaction count: {db_count}")
    
    # February 2025
    feb_sql = """
    SELECT SUM(credit) as total_credit, SUM(debit) as total_debit, COUNT(*) as count
    FROM general_ledger
    WHERE (LOWER(description) LIKE '%health%' 
           OR LOWER(vendor) LIKE '%health%'
           OR LOWER(description) LIKE '%insurance%'
           OR LOWER(vendor) LIKE '%insurance%')
      AND date >= '2025-02-01' 
      AND date <= '2025-02-28'
    """
    result = db.execute_query(feb_sql)
    if result:
        feb_db_credit = result[0]['total_credit'] or 0
        feb_db_debit = result[0]['total_debit'] or 0
        feb_db_count = result[0]['count'] or 0
        print(f"\n   February 2025 from DB:")
        print(f"     Credit (expenses): ${feb_db_credit:,.2f}")
        print(f"     Debit: ${feb_db_debit:,.2f}")
        print(f"     Transaction count: {feb_db_count}")
    
    # 4. Show sample transactions from both
    print("\n3. Sample transactions comparison:")
    print("   From CSV (first 5 health insurance entries):")
    for idx, row in health_df.head().iterrows():
        desc = row.get('Description', row.get('Memo/Description', ''))
        print(f"     {row['Date'].strftime('%Y-%m-%d')} - {desc} - Amount: {row['Amount']} (${row['Amount_Numeric']:,.2f})")
    
    print("\n   From DB (first 5 health insurance entries):")
    sample_sql = """
    SELECT date, description, vendor, credit, debit
    FROM general_ledger
    WHERE (LOWER(description) LIKE '%health%' 
           OR LOWER(vendor) LIKE '%health%'
           OR LOWER(description) LIKE '%insurance%'
           OR LOWER(vendor) LIKE '%insurance%')
    ORDER BY date DESC
    LIMIT 5
    """
    db_samples = db.execute_query(sample_sql)
    for row in db_samples:
        amount_str = f"Credit: ${row['credit']:,.2f}" if row['credit'] > 0 else f"Debit: ${row['debit']:,.2f}"
        print(f"     {row['date']} - {row['description']} - {amount_str}")
    
    # 5. Check for specific "Health Insurance" matches
    print("\n4. Exact 'Health Insurance' matches:")
    
    # In CSV
    exact_health_insurance_csv = df[df.apply(lambda row: any(
        'health insurance' in str(val).lower() 
        for val in row.values if pd.notna(val)
    ), axis=1)]
    
    print(f"   CSV entries with exact 'health insurance': {len(exact_health_insurance_csv)}")
    if len(exact_health_insurance_csv) > 0:
        total_exact = abs(exact_health_insurance_csv[exact_health_insurance_csv['Amount_Numeric'] < 0]['Amount_Numeric'].sum())
        print(f"   Total: ${total_exact:,.2f}")
    
    # In DB
    exact_sql = """
    SELECT SUM(credit) as total, COUNT(*) as count
    FROM general_ledger
    WHERE LOWER(description) LIKE '%health insurance%'
      AND credit > 0
    """
    result = db.execute_query(exact_sql)
    if result:
        db_exact_total = result[0]['total'] or 0
        db_exact_count = result[0]['count'] or 0
        print(f"\n   DB entries with exact 'health insurance': {db_exact_count}")
        print(f"   Total: ${db_exact_total:,.2f}")
    
    db.close()

if __name__ == "__main__":
    compare_csv_vs_db()