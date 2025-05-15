from crewai.tools import BaseTool
from typing import Type, Any, Optional, List, Dict
from pydantic import BaseModel, Field
import re
from pathlib import Path
import html
from email.parser import Parser
from email.header import decode_header

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
                    with open(email_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Clean and parse the content
                    cleaned_content = self._clean_email_content(content)
                    
                    # Simple search - case insensitive
                    if search_term.lower() in cleaned_content.lower():
                        # Extract relevant context (few lines around the match)
                        lines = cleaned_content.split('\n')
                        matching_sections = []
                        
                        for i, line in enumerate(lines):
                            if search_term.lower() in line.lower():
                                # Get context around the match
                                start = max(0, i-3)
                                end = min(len(lines), i+4)
                                context_lines = lines[start:end]
                                
                                # Clean up the context
                                context = '\n'.join(self._clean_lines(context_lines))
                                
                                matching_sections.append({
                                    'line_number': i,
                                    'context': context
                                })
                        
                        if matching_sections:
                            # Try to extract subject and date
                            subject = self._extract_subject(content)
                            date = self._extract_date(content)
                            
                            results.append({
                                'file': email_file.name,
                                'subject': subject,
                                'date': date,
                                'matches': matching_sections[:3]  # Limit to 3 matches per email
                            })
                
                except Exception as e:
                    continue  # Skip problematic files
            
            # Format results
            if results:
                output = [f"Email search results for '{search_term}':\n"]
                
                for result in results:
                    output.append(f"\n📧 Email: {result['file']}")
                    if result['subject']:
                        output.append(f"Subject: {result['subject']}")
                    if result['date']:
                        output.append(f"Date: {result['date']}")
                    
                    output.append("\nRelevant excerpts:")
                    for i, match in enumerate(result['matches'], 1):
                        output.append(f"\nExcerpt {i}:")
                        output.append(match['context'])
                        output.append("-" * 40)
                
                return '\n'.join(output)
            else:
                return f"No matches found for '{search_term}' in email files."
                
        except Exception as e:
            return f"Error searching emails: {str(e)}"
    
    def _clean_email_content(self, content: str) -> str:
        """Clean email content by removing HTML, encoding issues, etc."""
        # Decode HTML entities
        content = html.unescape(content)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', ' ', content)
        
        # Fix common encoding issues
        replacements = {
            '=E2=80=99': "'",  # Right single quotation mark
            '=E2=80=9C': '"',  # Left double quotation mark
            '=E2=80=9D': '"',  # Right double quotation mark
            '=E2=80=93': '-',  # En dash
            '=E2=80=94': '--', # Em dash
            '=C2=A0': ' ',     # Non-breaking space
            '=3D': '=',        # Equals sign
            '=20': ' ',        # Space
            '=\n': '',         # Soft line break
            '=0A': '\n',       # Line feed
            '&#39;': "'",      # Apostrophe
            '&amp;': '&',      # Ampersand
            '&lt;': '<',       # Less than
            '&gt;': '>',       # Greater than
            '&quot;': '"',     # Quote
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Remove quoted-printable encoding
        content = self._decode_quoted_printable(content)
        
        # Remove multiple spaces and clean up
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)  # Multiple blank lines to double
        
        # Remove email headers if present
        if 'Content-Type:' in content or 'MIME-Version:' in content:
            # Try to extract just the body
            content = self._extract_email_body(content)
        
        return content.strip()
    
    def _decode_quoted_printable(self, text: str) -> str:
        """Decode quoted-printable encoding"""
        try:
            # Handle quoted-printable sequences
            import quopri
            return quopri.decodestring(text.encode()).decode('utf-8', errors='ignore')
        except:
            return text
    
    def _extract_email_body(self, content: str) -> str:
        """Extract the body from a raw email"""
        try:
            # Find the start of the body (after headers)
            lines = content.split('\n')
            body_start = 0
            
            for i, line in enumerate(lines):
                if line.strip() == '':  # Empty line marks end of headers
                    body_start = i + 1
                    break
            
            return '\n'.join(lines[body_start:])
        except:
            return content
    
    def _extract_subject(self, content: str) -> Optional[str]:
        """Extract email subject from content"""
        # Try common patterns
        patterns = [
            r'Subject:\s*(.+?)(?:\n|$)',
            r'Re:\s*(.+?)(?:\n|$)',
            r'Fwd:\s*(.+?)(?:\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_date(self, content: str) -> Optional[str]:
        """Extract date from email content"""
        # Try common date patterns
        patterns = [
            r'Date:\s*(.+?)(?:\n|$)',
            r'(\w+\s+\d{1,2},\s+\d{4})',  # January 15, 2024
            r'(\d{1,2}/\d{1,2}/\d{4})',    # 01/15/2024
            r'(\d{4}-\d{2}-\d{2})',        # 2024-01-15
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _clean_lines(self, lines: List[str]) -> List[str]:
        """Clean individual lines of text"""
        cleaned = []
        for line in lines:
            # Skip certain line types
            if any(skip in line for skip in ['[image:', 'cid:', 'href=', '<img']):
                continue
            
            # Clean the line
            line = line.strip()
            if line and not line.startswith(('>', '>>>', 'Line ')):
                cleaned.append(line)
        
        return cleaned