# src/finbotics/parsers/ledger_parser.py (updated)
import pandas as pd
from typing import List, Dict, Any
import logging
from datetime import datetime
from src.finbotics.parsers.base_parser import BaseParser
from src.finbotics.db.sqlite_setup import SQLiteSetup

class GeneralLedgerParser(BaseParser):
    """Parser for General Ledger entries"""
    
    def __init__(self, db_setup: SQLiteSetup):
        super().__init__(db_setup)
        self.logger = logging.getLogger(__name__)

    # src/finbotics/parsers/ledger_parser.py (update parse_general_ledger method)

    def parse_general_ledger(self, file_path: str) -> None:
        """Parse General Ledger file and store in database"""
        self.logger.info(f"Parsing General Ledger file: {file_path}")
        
        try:
            # Read the CSV file
            df = self.read_csv_file(file_path)
            
            # Debug: print basic info about the file
            self.logger.info(f"File shape: {df.shape}")
            self.logger.info(f"Columns: {list(df.columns)}")
            
            # Check if file has data
            if len(df) == 0:
                self.logger.warning("General Ledger file has no data rows")
                return
            
            # Clean column names
            df.columns = df.columns.str.strip()
            
            # Parse the ledger entries
            records = self._parse_ledger_entries(df)
            
            if not records:
                self.logger.warning("No valid records found in General Ledger")
                # Debug: show why records might be empty
                self.logger.info(f"Sample row: {df.iloc[0].to_dict() if len(df) > 0 else 'No rows'}")
                return
                
            # Filter out invalid records
            valid_records = [r for r in records if self._validate_record(r)]
            invalid_count = len(records) - len(valid_records)
            
            if invalid_count > 0:
                self.logger.warning(f"Skipped {invalid_count} invalid records")
                
            # Clear existing data
            self.db_setup.clear_table('general_ledger')
            
            # Insert new data
            if valid_records:
                self.db_setup.insert_many('general_ledger', valid_records)
                self.logger.info(f"Inserted {len(valid_records)} records into general_ledger table")
            else:
                self.logger.warning("No valid records to insert into general_ledger")
                
        except Exception as e:
            self.logger.error(f"Error parsing general ledger: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
            raise

    def _parse_ledger_entries(self, df: pd.DataFrame) -> List[Dict]:
        """Parse ledger entries from dataframe"""
        records = []
        
        # Try to identify columns by common patterns
        column_mapping = self._identify_columns(df)
        self.logger.info(f"Column mapping: {column_mapping}")
        
        # Check if we have the minimum required columns
        if 'date' not in column_mapping:
            self.logger.error("Missing required 'date' column in mapping")
            return []
        
        for idx, row in df.iterrows():
            # Skip rows where all values are NaN
            if row.isnull().all():
                self.logger.debug(f"Skipping row {idx}: all values are NaN")
                continue
                
            try:
                record = self._parse_single_entry(row, column_mapping)
                if record:
                    records.append(record)
                else:
                    self.logger.debug(f"Failed to parse row {idx}")
            except Exception as e:
                self.logger.debug(f"Error parsing row {idx}: {str(e)}")
                continue
                
        self.logger.info(f"Successfully parsed {len(records)} records from {len(df)} rows")
        return records

    def _identify_columns(self, df: pd.DataFrame) -> Dict[str, str]:
        """Identify columns by patterns in column names"""
        mapping = {}
        
        # Debug: print actual column names
        self.logger.info(f"Actual columns in file: {list(df.columns)}")
        
        for col in df.columns:
            col_clean = col.strip()
            col_lower = col_clean.lower()
            
            # IMPORTANT: More precise column matching
            # Date column (exact match first)
            if col_clean == 'Date':
                mapping['date'] = col_clean
            # Transaction Type column
            elif col_clean == 'Transaction Type':
                mapping['transaction_type'] = col_clean
            # Category column
            elif col_clean == 'Category':
                mapping['category'] = col_clean
            # Name column (vendor/payee)
            elif col_clean == 'Name':
                mapping['vendor'] = col_clean
            # Description column  
            elif col_clean == 'Memo/Description':
                mapping['description'] = col_clean
            # Amount column
            elif col_clean == 'Amount':
                mapping['amount'] = col_clean
            # Balance column
            elif col_clean == 'Balance':
                mapping['balance'] = col_clean
            # Split column
            elif col_clean == 'Split':
                mapping['split'] = col_clean
            # Num column
            elif col_clean == 'Num':
                mapping['num'] = col_clean
            
        self.logger.info(f"Column mapping identified: {mapping}")
        return mapping
    
    def _parse_single_entry(self, row: pd.Series, column_mapping: Dict[str, str]) -> Dict:
        """Parse a single ledger entry"""
        record = {}
        
        # Date (required) - now using the correct column
        if 'date' in column_mapping:
            date_value = row.get(column_mapping['date'])
            if pd.notna(date_value):
                try:
                    # Handle various date formats
                    record['date'] = pd.to_datetime(date_value).strftime('%Y-%m-%d')
                except:
                    self.logger.debug(f"Could not parse date: {date_value}")
                    return None
            else:
                return None
        else:
            return None
        
        # Category -> Account
        if 'category' in column_mapping:
            category_value = row.get(column_mapping['category'])
            if pd.notna(category_value):
                record['account_name'] = str(category_value).strip()
                # Try to extract account code if present
                parts = str(category_value).split(' ', 1)
                if parts[0].isdigit():
                    record['account_code'] = parts[0]
                    record['account_name'] = parts[1] if len(parts) > 1 else category_value
                else:
                    record['account_code'] = None
        
        # Name -> Vendor
        if 'vendor' in column_mapping:
            vendor_value = row.get(column_mapping['vendor'])
            record['vendor'] = str(vendor_value).strip() if pd.notna(vendor_value) else None
        
        # Description
        if 'description' in column_mapping:
            desc_value = row.get(column_mapping['description'])
            record['description'] = str(desc_value).strip() if pd.notna(desc_value) else None
        
        # Amount (handle as either debit or credit)
        if 'amount' in column_mapping:
            amount_value = row.get(column_mapping['amount'])
            amount = self.parse_currency_value(amount_value)
            
            # Negative amounts are credits (expenses), positive are debits
            if amount < 0:
                record['credit'] = abs(amount)
                record['debit'] = 0.0
                record['transaction_type'] = 'credit'
            else:
                record['debit'] = amount
                record['credit'] = 0.0
                record['transaction_type'] = 'debit'
        else:
            record['debit'] = 0.0
            record['credit'] = 0.0
            record['transaction_type'] = 'other'
        
        # Balance
        if 'balance' in column_mapping:
            record['balance'] = self.parse_currency_value(row.get(column_mapping['balance']))
        
        # Transaction Type (additional info)
        if 'transaction_type' in column_mapping:
            trans_type = row.get(column_mapping['transaction_type'])
            if pd.notna(trans_type):
                record['reference_number'] = str(trans_type).strip()
        
        return record

    def _validate_record(self, record: Dict) -> bool:
        """Validate that a record has required fields"""
        required_fields = ['date', 'account_name']
        
        for field in required_fields:
            if field not in record or record[field] is None:
                self.logger.debug(f"Record missing required field '{field}': {record}")
                return False
                
        return True

    def validate_ledger(self) -> Dict[str, Any]:
        """Validate ledger entries for consistency"""
        validation_results = {
            'valid': True,
            'issues': [],
            'statistics': {}
        }
        
        try:
            # Get all records
            records = self.db_setup.execute_query("SELECT * FROM general_ledger ORDER BY date")
            
            # Basic statistics
            validation_results['statistics']['total_entries'] = len(records)
            
            if records:
                # Date range
                validation_results['statistics']['date_range'] = {
                    'start': records[0]['date'],
                    'end': records[-1]['date']
                }
                
                # Check balance continuity by account
                account_balances = {}
                balance_issues = []
                
                for record in records:
                    account = record['account_name']
                    
                    if account not in account_balances:
                        account_balances[account] = {
                            'running_balance': 0,
                            'last_recorded_balance': None,
                            'transactions': 0
                        }
                    
                    # Update running balance
                    debit = record.get('debit', 0) or 0
                    credit = record.get('credit', 0) or 0
                    account_balances[account]['running_balance'] += (debit - credit)
                    account_balances[account]['transactions'] += 1
                    
                    # Check if recorded balance matches running balance
                    if record.get('balance') is not None:
                        expected_balance = account_balances[account]['running_balance']
                        recorded_balance = record['balance']
                        
                        # Allow small rounding differences (0.01)
                        if abs(recorded_balance - expected_balance) > 0.01:
                            issue = {
                                'type': 'balance_mismatch',
                                'account': account,
                                'date': record['date'],
                                'expected': expected_balance,
                                'recorded': recorded_balance,
                                'difference': recorded_balance - expected_balance
                            }
                            balance_issues.append(issue)
                            validation_results['issues'].append(
                                f"Balance mismatch for {account} on {record['date']}: "
                                f"Expected {expected_balance:.2f}, got {recorded_balance:.2f}"
                            )
                            validation_results['valid'] = False
                    
                    account_balances[account]['last_recorded_balance'] = record.get('balance')
                
                # Account statistics
                validation_results['statistics']['unique_accounts'] = len(account_balances)
                validation_results['statistics']['accounts_with_activity'] = {
                    account: info['transactions'] 
                    for account, info in account_balances.items() 
                    if info['transactions'] > 0
                }
                
                # Vendor statistics
                vendor_query = """
                    SELECT vendor, COUNT(*) as count, SUM(credit) as total_credit
                    FROM general_ledger
                    WHERE vendor IS NOT NULL
                    GROUP BY vendor
                    ORDER BY total_credit DESC
                """
                vendor_stats = self.db_setup.execute_query(vendor_query)
                validation_results['statistics']['unique_vendors'] = len(vendor_stats)
                validation_results['statistics']['top_vendors'] = [
                    {
                        'vendor': v['vendor'],
                        'transactions': v['count'],
                        'total_spent': v['total_credit']
                    }
                    for v in vendor_stats[:5]  # Top 5 vendors
                ]
                
                # Transaction type breakdown
                type_query = """
                    SELECT transaction_type, COUNT(*) as count
                    FROM general_ledger
                    GROUP BY transaction_type
                """
                type_stats = self.db_setup.execute_query(type_query)
                validation_results['statistics']['transaction_types'] = {
                    t['transaction_type']: t['count'] 
                    for t in type_stats
                }
                
                # Monthly summary
                monthly_query = """
                    SELECT 
                        strftime('%Y-%m', date) as month,
                        COUNT(*) as transactions,
                        SUM(debit) as total_debit,
                        SUM(credit) as total_credit
                    FROM general_ledger
                    GROUP BY strftime('%Y-%m', date)
                    ORDER BY month
                """
                monthly_stats = self.db_setup.execute_query(monthly_query)
                validation_results['statistics']['monthly_summary'] = monthly_stats
                
                # Check for potential duplicates
                duplicate_query = """
                    SELECT date, account_name, description, debit, credit, COUNT(*) as count
                    FROM general_ledger
                    GROUP BY date, account_name, description, debit, credit
                    HAVING COUNT(*) > 1
                """
                duplicates = self.db_setup.execute_query(duplicate_query)
                if duplicates:
                    validation_results['issues'].append(f"Found {len(duplicates)} potential duplicate entries")
                    validation_results['statistics']['potential_duplicates'] = len(duplicates)
                
            else:
                validation_results['issues'].append("No ledger entries found")
                validation_results['valid'] = False
                
        except Exception as e:
            validation_results['valid'] = False
            validation_results['issues'].append(f"Validation error: {str(e)}")
            self.logger.error(f"Error validating ledger: {str(e)}")
            
        return validation_results
