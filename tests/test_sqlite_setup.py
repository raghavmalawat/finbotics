# tests/test_sqlite_setup.py
from src.finbotics.db.sqlite_setup import SQLiteSetup
from src.finbotics.utils.logging_config import setup_logging

def test_sqlite_setup():
    """Test SQLite connection and setup"""
    setup_logging("INFO")
    
    # Initialize and connect
    db_setup = SQLiteSetup()
    db_setup.connect()
    
    # Setup tables
    db_setup.setup_tables()
    
    # Test table access
    tables = ['profit_loss', 'balance_sheet', 'general_ledger', 'expense_summary']
    for table in tables:
        count = db_setup.execute_query(f"SELECT COUNT(*) as count FROM {table}")
        print(f"{table}: {count[0]['count']} records")
    
    print("SQLite setup completed successfully!")

if __name__ == "__main__":
    test_sqlite_setup()