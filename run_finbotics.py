# run_finbotics.py
import os
import sys
from pathlib import Path
import logging
from src.finbotics.parsers.financial_parser import FinancialStatementParser
from src.finbotics.utils.logging_config import setup_logging

def initialize_database():
    """Initialize the database with financial data"""
    print("Initializing Finbotics database...")
    
    # Setup logging
    setup_logging("INFO")
    
    # Create parser
    parser = FinancialStatementParser()
    
    # Parse all files
    data_dir = "data/csv"
    if not Path(data_dir).exists():
        print(f"Error: Data directory {data_dir} not found!")
        print("Please ensure your CSV files are in the data/csv directory.")
        return False
    
    try:
        results = parser.parse_all_files(data_dir)
        
        # Print summary
        print("\nDatabase initialization complete!")
        print("\nSummary:")
        for file_type, result in results.items():
            if isinstance(result, dict):
                if 'statistics' in result:
                    stats = result['statistics']
                    if file_type == 'expense_summary':
                        print(f"  {file_type}: {stats.get('total_vendors', 0)} vendors loaded")
                    elif file_type == 'general_ledger':
                        print(f"  {file_type}: {stats.get('total_entries', 0)} entries loaded")
                    else:
                        print(f"  {file_type}: {stats.get('total_records', 0)} records loaded")
        
        return True
        
    except Exception as e:
        print(f"Error initializing database: {str(e)}")
        logging.error(f"Database initialization failed: {str(e)}")
        return False

def launch_ui():
    """Launch the Streamlit UI"""
    print("\nLaunching Finbotics UI...")
    print("Opening in your default browser...")
    os.system("streamlit run app.py")

def main():
    """Main entry point"""
    print("Welcome to Finbotics - AI Financial Assistant")
    print("=" * 50)
    
    # Check if database exists
    db_path = Path("data/finbotics.db")
    
    if not db_path.exists():
        print("Database not found. Initializing...")
        if not initialize_database():
            print("Failed to initialize database. Exiting.")
            sys.exit(1)
    else:
        print("Database found.")
        response = input("Reinitialize database? (y/N): ")
        if response.lower() == 'y':
            if not initialize_database():
                print("Failed to initialize database. Exiting.")
                sys.exit(1)
    
    # Launch UI
    launch_ui()

if __name__ == "__main__":
    main()