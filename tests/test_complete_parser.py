# tests/test_complete_parser.py
from src.finbotics.parsers.financial_parser import FinancialStatementParser
from src.finbotics.queries.hierarchy_queries import HierarchyQueryHelper
from src.finbotics.queries.ledger_queries import LedgerQueryHelper, ExpenseQueryHelper
from src.finbotics.utils.logging_config import setup_logging
import json

def test_complete_parsing():
    """Test parsing all financial files"""
    setup_logging("INFO")
    
    # Initialize parser
    parser = FinancialStatementParser()
    
    # Parse all files
    print("Parsing all financial files...")
    results = parser.parse_all_files("data/csv")
    
    print("\n=== Parsing Results ===")
    for file_type, result in results.items():
        print(f"\n{file_type}:")
        print(json.dumps(result, indent=2, default=str))
    
    # Test queries
    print("\n\n=== Testing Queries ===")
    
    # Test hierarchy queries
    hierarchy_helper = HierarchyQueryHelper(parser.db_setup)
    print("\n1. Income Analysis:")
    income_total = hierarchy_helper.calculate_category_total('profit_loss', 'Income', '2024-01')
    print(f"   Total Income (Jan 2024): ${income_total:,.2f}")
    
    # Test ledger queries
    ledger_helper = LedgerQueryHelper(parser.db_setup)
    print("\n2. Vendor Transactions:")
    vendor_transactions = ledger_helper.get_transactions_by_vendor('OpenAI', '2024-01-01', '2024-12-31')
    print(f"   Found {len(vendor_transactions)} transactions for OpenAI")
    for trans in vendor_transactions[:3]:  # Show first 3
        print(f"   - {trans['date']}: ${trans['credit']:,.2f} - {trans['description']}")
    
    # Test expense queries
    expense_helper = ExpenseQueryHelper(parser.db_setup)
    print("\n3. Top Vendors:")
    top_vendors = parser.expense_parser.get_top_vendors(5)
    for vendor in top_vendors:
        print(f"   - {vendor['vendor_name']}: ${vendor['total']:,.2f}")
    
    # Test account balance
    print("\n4. Account Balance:")
    balance = ledger_helper.calculate_account_balance('Cash', '2024-12-31')
    print(f"   Cash balance as of 2024-12-31: ${balance:,.2f}")
    
    # Test monthly summary
    print("\n5. Monthly Summary:")
    monthly_summary = ledger_helper.get_monthly_summary(2024, 1)
    print(f"   January 2024:")
    print(f"   - Transactions: {monthly_summary.get('transaction_count', 0)}")
    print(f"   - Total Debits: ${monthly_summary.get('total_debits') or 0:,.2f}")
    print(f"   - Total Credits: ${monthly_summary.get('total_credits') or 0:,.2f}")
    
    print("\n\nAll tests completed successfully!")


if __name__ == "__main__":
    test_complete_parsing()