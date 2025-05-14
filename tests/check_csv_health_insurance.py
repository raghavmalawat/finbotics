# tests/check_csv_health_insurance.py
import pandas as pd

def check_csv_health_insurance():
    """Check how health insurance appears in the CSV"""
    
    # Read the general ledger CSV
    df = pd.read_csv('data/csv/general_ledger.csv')
    
    print("=== Health Insurance in CSV ===\n")
    
    # Check column names
    print(f"Columns: {list(df.columns)}\n")
    
    # Look for health insurance in different columns
    for col in df.columns:
        if col in ['Description', 'Memo/Description', 'Category', 'Name', 'Vendor']:
            print(f"Checking column: {col}")
            
            # Find rows containing health/insurance
            mask = df[col].astype(str).str.lower().str.contains('health|insurance|benefit', na=False)
            health_rows = df[mask]
            
            if not health_rows.empty:
                print(f"Found {len(health_rows)} rows:")
                for idx, row in health_rows.head(5).iterrows():
                    print(f"  {row['Date']} - {col}: {row[col]} - Amount: {row.get('Amount', 'N/A')}")
                print()
    
    # Check February 2024 data specifically
    print("\nFebruary 2024 entries:")
    feb_mask = pd.to_datetime(df['Date']).dt.to_period('M') == '2024-02'
    feb_df = df[feb_mask]
    
    print(f"Total February entries: {len(feb_df)}")
    
    # Look for health insurance in February
    health_feb_mask = feb_df.apply(lambda row: any('health' in str(val).lower() or 'insurance' in str(val).lower() 
                                                   for val in row.values), axis=1)
    health_feb = feb_df[health_feb_mask]
    
    if not health_feb.empty:
        print(f"Found {len(health_feb)} health insurance entries in February:")
        for idx, row in health_feb.iterrows():
            print(f"  {row['Date']} - {row.get('Description', row.get('Memo/Description'))} - Amount: {row.get('Amount')}")
    else:
        print("No health insurance entries found in February")

if __name__ == "__main__":
    check_csv_health_insurance()