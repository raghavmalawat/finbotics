from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import pandas as pd

class FinancialFormatterInput(BaseModel):
    """Input schema for Financial Formatter Tool"""
    data: str = Field(description="Financial data to format")
    format_type: str = Field(description="Type of formatting: 'currency', 'percentage', 'summary'")

class FinancialFormatterTool(BaseTool):
    name: str = "Financial Data Formatter"
    description: str = "Formats financial data for better readability"
    args_schema: Type[BaseModel] = FinancialFormatterInput
    
    def _run(self, data: str, format_type: str) -> str:
        """Format financial data based on type"""
        try:
            if format_type == "currency":
                # Parse and format currency values
                lines = data.strip().split('\n')
                formatted_lines = []
                for line in lines:
                    if '$' in line or any(char.isdigit() for char in line):
                        # Simple currency formatting
                        formatted_lines.append(line)
                    else:
                        formatted_lines.append(line)
                return '\n'.join(formatted_lines)
            
            elif format_type == "summary":
                # Create a summary format
                return f"=== Financial Summary ===\n{data}\n" + "="*23
                
            else:
                return data
                
        except Exception as e:
            return f"Formatting error: {str(e)}\nOriginal data: {data}"
