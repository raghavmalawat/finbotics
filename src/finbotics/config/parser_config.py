from dataclasses import dataclass
from typing import Dict, List

@dataclass
class ParserConfig:
    """Configuration for financial parsers"""
    
    # File paths
    profit_loss_path: str = "data/csv/profit_loss.csv"
    balance_sheet_path: str = "data/csv/balance_sheet.csv"
    general_ledger_path: str = "data/csv/general_ledger.csv"
    expense_summary_path: str = "data/csv/expense_summary.csv"
    
    # MongoDB settings
    mongodb_uri: str = "mongodb://localhost:27017/"
    database_name: str = "finbotics"
    
    # Parser settings
    indent_size: int = 2  # Number of spaces per hierarchy level
    max_hierarchy_depth: int = 5
    
    # Column mappings for different files
    column_mappings: Dict[str, Dict[str, str]] = None
    
    def __post_init__(self):
        if self.column_mappings is None:
            self.column_mappings = {
                'general_ledger': {
                    'date': 'Date',
                    'account': 'Account',
                    'description': 'Description',
                    'vendor': 'Vendor',
                    'debit': 'Debit',
                    'credit': 'Credit',
                    'balance': 'Balance'
                },
                'expense_summary': {
                    'vendor': 'Vendor',
                    'category': 'Category',
                    'total': 'Total'
                }
            }