# tests/check_database.py
from src.finbotics.db.sqlite_setup import SQLiteSetup
import json

def check_database_contents():
    """Check what's actually in the database"""
    
    db = SQLiteSetup()
    db.connect()
    
    tables = ['profit_loss', 'balance_sheet', 'general_ledger', 'expense_summary']
    
    for table in tables:
        print(f"\n{'='*50}")
        print(f"TABLE: {table}")
        print('='*50)
        
        # Count records
        count_query = f"SELECT COUNT(*) as count FROM {table}"
        count_result = db.execute_query(count_query)
        print(f"Total records: {count_result[0]['count']}")
        
        # Sample records
        sample_query = f"SELECT * FROM {table} LIMIT 5"
        sample_results = db.execute_query(sample_query)
        
        if sample_results:
            print("\nSample records:")
            for i, record in enumerate(sample_results):
                print(f"\nRecord {i+1}:")
                for key, value in record.items():
                    if key == 'values_json' and value:
                        try:
                            parsed = json.loads(value)
                            print(f"  {key}: {parsed}")
                        except:
                            print(f"  {key}: {value}")
                    else:
                        print(f"  {key}: {value}")
        else:
            print("No records found")
            
        # For tables with values_json, check date keys
        if table in ['profit_loss', 'balance_sheet', 'expense_summary']:
            date_query = f"SELECT values_json FROM {table} LIMIT 1"
            date_results = db.execute_query(date_query)
            if date_results and date_results[0]['values_json']:
                try:
                    values = json.loads(date_results[0]['values_json'])
                    print(f"\nDate keys in values_json: {list(values.keys())[:5]}")
                except:
                    pass
    
    db.close()

if __name__ == "__main__":
    check_database_contents()