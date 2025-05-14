from crewai.tools import BaseTool
from typing import Type, Any, Optional
from pydantic import BaseModel, Field
import re
from pathlib import Path

class EmailSearchInput(BaseModel):
    """Input schema for Email Search Tool"""
    search_term: str = Field(description="Term to search for in emails")
    email_directory: str = Field(default="data/emails", description="Directory containing email files")

class EmailSearchTool(BaseTool):
    name: str = "Email Search Tool"
    description: str = "Searches through email files for specific terms and context"
    args_schema: Type[BaseModel] = EmailSearchInput
    
    def _run(self, search_term: str, email_directory: str = "data/emails") -> str:
        """Search through email files for the specified term"""
        try:
            email_dir = Path(email_directory)
            results = []
            email_files = list(email_dir.glob("*.txt"))
            
            for email_file in email_files:
                try:
                    with open(email_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Simple search - case insensitive
                    if search_term.lower() in content.lower():
                        # Extract relevant context (few lines around the match)
                        lines = content.split('\n')
                        matching_lines = []
                        
                        for i, line in enumerate(lines):
                            if search_term.lower() in line.lower():
                                # Get 2 lines before and after for context
                                start = max(0, i-2)
                                end = min(len(lines), i+3)
                                context = '\n'.join(lines[start:end])
                                matching_lines.append({
                                    'file': email_file.name,
                                    'line_number': i,
                                    'context': context
                                })
                        
                        if matching_lines:
                            results.append({
                                'file': email_file.name,
                                'matches': matching_lines
                            })
                
                except Exception as e:
                    results.append({
                        'file': email_file.name,
                        'error': str(e)
                    })
            
            # Format results
            if results:
                output = f"Email search results for '{search_term}':\n\n"
                for result in results:
                    output += f"File: {result['file']}\n"
                    if 'matches' in result:
                        for match in result['matches']:
                            output += f"  Line {match['line_number']}:\n"
                            output += f"  {match['context']}\n\n"
                    elif 'error' in result:
                        output += f"  Error: {result['error']}\n\n"
                return output
            else:
                return f"No matches found for '{search_term}' in email files."
                
        except Exception as e:
            return f"Error searching emails: {str(e)}"