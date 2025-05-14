# src/finbotics/db/sqlite_setup.py
import sqlite3
from pathlib import Path
import logging
from typing import List, Dict, Any, Optional
import json

class SQLiteSetup:
    """SQLite connection and setup manager"""
    
    def __init__(self, db_path: str = None):
        """Initialize SQLite connection"""
        self.db_path = db_path or "data/finbotics.db"
        self.conn = None
        self.logger = logging.getLogger(__name__)
        
        # Ensure directory exists
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
    def connect(self) -> None:
        """Establish connection to SQLite"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            self.logger.info(f"Connected to SQLite: {self.db_path}")
        except Exception as e:
            self.logger.error(f"Failed to connect to SQLite: {str(e)}")
            raise
            
    def setup_tables(self) -> None:
        """Create tables and indexes"""
        cursor = self.conn.cursor()
        
        # Profit & Loss table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS profit_loss (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name TEXT NOT NULL,
                category_path TEXT NOT NULL,
                parent_category TEXT,
                level INTEGER NOT NULL,
                is_parent BOOLEAN DEFAULT FALSE,
                is_total BOOLEAN DEFAULT FALSE,
                line_type TEXT CHECK(line_type IN ('detail', 'parent', 'total')),
                values_json TEXT NOT NULL,  -- JSON storing all date-value pairs
                row_number INTEGER,
                indentation_level INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Balance Sheet table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS balance_sheet (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                account_name TEXT NOT NULL,
                account_path TEXT NOT NULL,
                account_type TEXT CHECK(account_type IN ('asset', 'liability', 'equity')),
                parent_account TEXT,
                level INTEGER NOT NULL,
                is_parent BOOLEAN DEFAULT FALSE,
                is_total BOOLEAN DEFAULT FALSE,
                values_json TEXT NOT NULL,  -- JSON storing all date-value pairs
                row_number INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # General Ledger table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS general_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date DATE NOT NULL,
                account_code TEXT,
                account_name TEXT NOT NULL,
                description TEXT,
                vendor TEXT,
                debit REAL DEFAULT 0,
                credit REAL DEFAULT 0,
                balance REAL,
                transaction_type TEXT,
                reference_number TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Expense Summary table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expense_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                vendor_name TEXT NOT NULL,
                category TEXT,
                values_json TEXT NOT NULL,  -- JSON storing monthly values
                total REAL,
                payment_terms TEXT,
                vendor_type TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for better query performance
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_pl_category_path ON profit_loss(category_path)",
            "CREATE INDEX IF NOT EXISTS idx_pl_parent ON profit_loss(parent_category)",
            "CREATE INDEX IF NOT EXISTS idx_pl_level ON profit_loss(level)",
            "CREATE INDEX IF NOT EXISTS idx_bs_account_path ON balance_sheet(account_path)",
            "CREATE INDEX IF NOT EXISTS idx_bs_type ON balance_sheet(account_type)",
            "CREATE INDEX IF NOT EXISTS idx_gl_date ON general_ledger(date)",
            "CREATE INDEX IF NOT EXISTS idx_gl_vendor ON general_ledger(vendor)",
            "CREATE INDEX IF NOT EXISTS idx_gl_account ON general_ledger(account_name)",
            "CREATE INDEX IF NOT EXISTS idx_es_vendor ON expense_summary(vendor_name)",
            "CREATE INDEX IF NOT EXISTS idx_es_total ON expense_summary(total DESC)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
            
        self.conn.commit()
        self.logger.info("Tables and indexes created successfully")
        
    def clear_table(self, table_name: str) -> None:
        """Clear all records from a table"""
        cursor = self.conn.cursor()
        cursor.execute(f"DELETE FROM {table_name}")
        self.conn.commit()
        self.logger.info(f"Cleared table: {table_name}")
        
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries"""
        cursor = self.conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
            
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    def insert_many(self, table_name: str, records: List[Dict[str, Any]]) -> None:
        """Bulk insert records into a table"""
        if not records:
            return
            
        cursor = self.conn.cursor()
        columns = records[0].keys()
        placeholders = ', '.join(['?' for _ in columns])
        column_names = ', '.join(columns)
        
        query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"
        values = [tuple(record.values()) for record in records]
        
        cursor.executemany(query, values)
        self.conn.commit()
        self.logger.info(f"Inserted {len(records)} records into {table_name}")
        
    def close(self) -> None:
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.logger.info("Database connection closed")