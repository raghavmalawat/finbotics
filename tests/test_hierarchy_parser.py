# tests/test_hierarchy_parser.py
from src.finbotics.parsers.financial_parser import FinancialStatementParser
from src.finbotics.queries.hierarchy_queries import HierarchyQueryHelper
from src.finbotics.utils.logging_config import setup_logging
import json

def test_hierarchy_parser():
    """Test the hierarchy parser"""
    setup_logging("INFO")
    
    # Initialize parser
    parser = FinancialStatementParser()
    
    # Parse files
    results = parser.parse_all_files("data/csv")
    
    print("\nParsing Results:")
    print(json.dumps(results, indent=2))
    
    # Test queries
    query_helper = HierarchyQueryHelper(parser.db_setup)
    
    # Test P&L queries
    print("\n\nP&L Hierarchy:")
    income_records = query_helper.get_category_with_children('profit_loss', 'Income')
    for record in income_records[:5]:  # Show first 5
        print(f"  {'  ' * record['level']}{record['category_name']}: {record['line_type']}")
    
    # Test balance calculation
    total_income = query_helper.calculate_category_total('profit_loss', 'Income', '2024-01')
    print(f"\nTotal Income for 2024-01: ${total_income:,.2f}")
    
    # Test Balance Sheet queries
    print("\n\nBalance Sheet Structure:")
    assets = query_helper.get_category_with_children('balance_sheet', 'Assets')
    for record in assets[:5]:  # Show first 5
        print(f"  {'  ' * record['level']}{record['account_name']}: {record['account_type']}")
    
    # Test time series
    print("\n\nTime Series Example:")
    time_series = query_helper.get_time_series('profit_loss', 'Total Revenue')
    for date, value in list(time_series.items())[:3]:
        print(f"  {date}: ${value:,.2f}")
    
    print("\n\nHierarchy parsing completed successfully!")

if __name__ == "__main__":
    test_hierarchy_parser()