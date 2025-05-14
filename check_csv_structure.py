# check_csv_structure.py
import pandas as pd
from pathlib import Path

def check_csv_files():
    """Check the structure of our CSV files"""
    
    csv_dir = Path("data/csv")
    csv_files = list(csv_dir.glob("*.csv"))
    
    for csv_file in csv_files:
        print(f"\n{'='*50}")
        print(f"File: {csv_file.name}")
        print('='*50)
        
        try:
            df = pd.read_csv(csv_file)
            print(f"Shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            print(f"\nFirst 3 rows:")
            print(df.head(3))
            print(f"\nData types:")
            print(df.dtypes)
        except Exception as e:
            print(f"Error reading file: {e}")

if __name__ == "__main__":
    check_csv_files()