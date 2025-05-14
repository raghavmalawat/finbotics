# tests/debug_general_ledger.py
import pandas as pd
from pathlib import Path

def debug_general_ledger():
    """Debug the general ledger CSV structure"""
    file_path = "data/csv/general_ledger.csv"
    
    if not Path(file_path).exists():
        print(f"File not found: {file_path}")
        return
    
    # Read CSV
    df = pd.read_csv(file_path)
    
    print("=== General Ledger Debug ===")
    print(f"Shape: {df.shape}")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst 10 rows:")
    print(df.head(10))
    print(f"\nData types:")
    print(df.dtypes)
    
    # Check for null values
    print(f"\nNull values per column:")
    print(df.isnull().sum())
    
    # Check sample values for each column
    print(f"\nSample non-null values per column:")
    for col in df.columns:
        non_null_values = df[col].dropna().unique()[:5]
        print(f"{col}: {non_null_values}")
    
    # Check if file is empty or has only headers
    if len(df) == 0:
        print("\nWARNING: File appears to be empty (no data rows)")
    
    # Save a sample for inspection
    df.head(20).to_csv('debug_general_ledger_sample.csv', index=False)
    print("\nSaved sample to debug_general_ledger_sample.csv")

if __name__ == "__main__":
    debug_general_ledger()