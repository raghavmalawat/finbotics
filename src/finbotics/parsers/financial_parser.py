# src/finbotics/parsers/financial_parser.py (updated)
from pathlib import Path
from typing import Dict, Any
import logging
from src.finbotics.parsers.hierarchy_parser import HierarchyParser
from src.finbotics.parsers.ledger_parser import GeneralLedgerParser
from src.finbotics.parsers.expense_parser import ExpenseSummaryParser
from src.finbotics.db.sqlite_setup import SQLiteSetup

class FinancialStatementParser:
    """Main parser for all financial statements"""
    
    def __init__(self, db_path: str = None):
        self.db_setup = SQLiteSetup(db_path)
        self.db_setup.connect()
        self.db_setup.setup_tables()
        
        self.hierarchy_parser = HierarchyParser(self.db_setup)
        self.ledger_parser = GeneralLedgerParser(self.db_setup)
        self.expense_parser = ExpenseSummaryParser(self.db_setup)
        self.logger = logging.getLogger(__name__)
        
    def parse_all_files(self, data_dir: str = "data/csv") -> Dict[str, Any]:
        """Parse all financial files in the directory"""
        data_path = Path(data_dir)
        results = {}
        
        # File mappings
        file_mappings = {
            'profit_loss': ['profit_loss.csv', 'profit_loss.xlsx'],
            'balance_sheet': ['balance_sheet.csv', 'balance_sheet.xlsx'],
            'general_ledger': ['general_ledger.csv', 'general_ledger.xlsx'],
            'expense_summary': ['expense_summary.csv', 'expense_summary.xlsx']
        }
        
        # Parse P&L
        pl_files = [f for f in file_mappings['profit_loss'] if (data_path / f).exists()]
        if pl_files:
            pl_file = data_path / pl_files[0]
            self.logger.info(f"Parsing P&L file: {pl_file}")
            self.hierarchy_parser.parse_profit_loss(str(pl_file))
            results['profit_loss'] = self.hierarchy_parser.validate_hierarchy('profit_loss')
        
        # Parse Balance Sheet
        bs_files = [f for f in file_mappings['balance_sheet'] if (data_path / f).exists()]
        if bs_files:
            bs_file = data_path / bs_files[0]
            self.logger.info(f"Parsing Balance Sheet file: {bs_file}")
            self.hierarchy_parser.parse_balance_sheet(str(bs_file))
            results['balance_sheet'] = self.hierarchy_parser.validate_hierarchy('balance_sheet')
        
        # Parse General Ledger
        gl_files = [f for f in file_mappings['general_ledger'] if (data_path / f).exists()]
        if gl_files:
            gl_file = data_path / gl_files[0]
            self.logger.info(f"Parsing General Ledger file: {gl_file}")
            self.ledger_parser.parse_general_ledger(str(gl_file))
            results['general_ledger'] = self.ledger_parser.validate_ledger()
        
        # Parse Expense Summary
        es_files = [f for f in file_mappings['expense_summary'] if (data_path / f).exists()]
        if es_files:
            es_file = data_path / es_files[0]
            self.logger.info(f"Parsing Expense Summary file: {es_file}")
            self.expense_parser.parse_expense_summary(str(es_file))
            results['expense_summary'] = self.expense_parser.validate_expense_summary()
        
        return results