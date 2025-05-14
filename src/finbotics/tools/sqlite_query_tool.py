# src/finbotics/tools/sqlite_query_tool.py (no changes needed, but ensure it doesn't have extra attributes)
from crewai.tools import BaseTool
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field
import sqlite3
import json
import logging

class SQLiteQueryInput(BaseModel):
    """Input for SQLite Query Tool"""
    query: str = Field(description="SQL query to execute")
    params: List[Any] = Field(default=[], description="Query parameters")
    database_path: str = Field(default="data/finbotics.db", description="Path to SQLite database")

class SQLiteQueryTool(BaseTool):
    name: str = "SQLite Query Tool"
    description: str = "Executes SQL queries on the financial database and returns results"
    args_schema: Type[BaseModel] = SQLiteQueryInput
    
    def _run(self, query: str, params: List[Any] = None, database_path: str = "data/finbotics.db") -> str:
        """Execute SQL query and return results"""
        try:
            # Connect to database
            conn = sqlite3.connect(database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Execute query
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # Fetch results
            if query.strip().upper().startswith('SELECT'):
                rows = cursor.fetchall()
                results = [dict(row) for row in rows]
                
                # Format results
                if not results:
                    return "No results found."
                
                # Convert to readable format
                formatted_results = []
                for row in results[:10]:  # Limit to 10 rows for readability
                    formatted_row = {}
                    for key, value in row.items():
                        if key == 'values_json' and value:
                            try:
                                formatted_row[key] = json.loads(value)
                            except:
                                formatted_row[key] = value
                        else:
                            formatted_row[key] = value
                    formatted_results.append(formatted_row)
                
                return json.dumps(formatted_results, indent=2, default=str)
            else:
                conn.commit()
                return f"Query executed successfully. Rows affected: {cursor.rowcount}"
                
        except Exception as e:
            return f"Error executing query: {str(e)}"
        finally:
            if 'conn' in locals():
                conn.close()