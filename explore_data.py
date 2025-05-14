import pandas as pd
from pathlib import Path

def explore_excel_files():
    """Explore the structure of our Excel files"""
    
    data_dir = Path("data/excel")
    
    files = [
        "Acme+AI_General+Ledger.xlsx",
        "Acme+AI_Expenses+by+Vendor+Summary.xlsx",
        "Acme+AI_Balance+Sheet.xlsx",
        "Acme+AI_Profit+and+Loss.xlsx"
    ]
    
    for file in files:
        file_path = data_dir / file
        if file_path.exists():
            print(f"\n{'='*50}")
            print(f"File: {file}")
            print('='*50)
            
            try:
                df = pd.read_excel(file_path)
                print(f"Shape: {df.shape}")
                print(f"Columns: {list(df.columns)}")
                print(f"\nFirst few rows:")
                print(df.head())
                print(f"\nData types:")
                print(df.dtypes)
            except Exception as e:
                print(f"Error reading file: {e}")

if __name__ == "__main__":
    explore_excel_files()