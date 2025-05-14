# tests/debug_files.py
import pandas as pd
from pathlib import Path

def debug_all_files():
    """Debug all financial files to understand their structure"""
    
    files = [
        "data/csv/profit_loss.csv",
        "data/csv/balance_sheet.csv", 
        "data/csv/general_ledger.csv",
        "data/csv/expense_summary.csv"
    ]
    
    for file_path in files:
        print(f"\n{'='*50}")
        print(f"FILE: {file_path}")
        print('='*50)
        
        if Path(file_path).exists():
            # Read first few rows
            df = pd.read_csv(file_path, nrows=10)
            
            print(f"Shape: {df.shape}")
            print(f"\nColumns: {list(df.columns)}")
            print(f"\nFirst 5 rows:")
            print(df.head())
            print(f"\nData types:")
            print(df.dtypes)
            
            # Check for date columns
            print(f"\nPotential date columns:")
            for col in df.columns:
                sample_value = df[col].iloc[0] if len(df) > 0 else None
                print(f"  {col}: {sample_value}")
        else:
            print(f"File not found: {file_path}")

if __name__ == "__main__":
    debug_all_files()