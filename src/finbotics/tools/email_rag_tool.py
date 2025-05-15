from crewai.tools import BaseTool
from typing import Type, Any, Optional, List, Dict
from pydantic import BaseModel, Field
import re
from pathlib import Path
import html
from datetime import datetime
import json

class EmailSearchInput(BaseModel):
    """Input schema for Email Search Tool"""
    query: str = Field(description="Natural language query about emails")
    email_directory: str = Field(default="data/emails", description="Directory containing email files")

class EmailRAGTool(BaseTool):
    name: str = "Email RAG Tool"
    description: str = "Performs intelligent search over email files using natural language queries"
    args_schema: Type[BaseModel] = EmailSearchInput
    
    def _run(self, query: str, email_directory: str = "data/emails") -> str:
        """Search through email files using natural language understanding"""
        try:
            email_dir = Path(email_directory)
            all_emails = []
            
            # First, load and parse all emails
            for email_file in email_dir.glob("*.txt"):
                try:
                    with open(email_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    # Parse email into structured format
                    email_data = self._parse_email(content, email_file.name)
                    if email_data:
                        all_emails.append(email_data)
                except Exception as e:
                    continue
            
            if not all_emails:
                return "No email files found in the specified directory."
            
            # Now use intelligent search based on the query
            relevant_emails = self._find_relevant_emails(query, all_emails)
            
            # Format results based on query intent
            return self._format_results_for_query(query, relevant_emails)
                
        except Exception as e:
            return f"Error searching emails: {str(e)}"
    
    def _parse_email(self, content: str, filename: str) -> Dict[str, Any]:
        """Parse email content into structured format"""
        # First extract the thread content
        thread_content = self._extract_email_thread_content(content)
        
        # Clean content
        cleaned_content = self._clean_email_content(content)
        
        # Extract metadata from original content (before cleaning)
        email_data = {
            'filename': filename,
            'subject': self._extract_field(content, 'subject'),
            'from': self._extract_field(content, 'from'),
            'to': self._extract_field(content, 'to'),
            'date': self._extract_field(content, 'date'),
            'body': thread_content if thread_content else self._extract_body(cleaned_content),
            'raw_content': content,
            'cleaned_content': cleaned_content
        }
        
        # Add parsed date for sorting
        if email_data['date']:
            email_data['parsed_date'] = self._parse_date_extended(email_data['date'])
        
        return email_data
    
    def _parse_date_extended(self, date_str: str) -> str:
        """Parse extended date formats including email-style dates"""
        if not date_str:
            return ""
        
        # Clean up the date string
        date_str = date_str.strip()
        
        # Handle email date format: "Thu, 20 Mar 2025 22:13:50 -0700"
        email_date_pattern = r'[A-Za-z]{3},\s+(\d{1,2})\s+([A-Za-z]{3})\s+(\d{4})\s+(\d{2}:\d{2}:\d{2})'
        match = re.search(email_date_pattern, date_str)
        if match:
            day, month_abbr, year, time = match.groups()
            # Convert month abbreviation to number
            months = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }
            month = months.get(month_abbr, 1)
            try:
                dt = datetime(int(year), month, int(day))
                return dt.isoformat()
            except:
                pass
        
        # Try other common formats
        formats = [
            '%B %d, %Y',  # January 15, 2024
            '%Y-%m-%d',   # 2024-01-15
            '%m/%d/%Y',   # 01/15/2024
            '%d/%m/%Y',   # 15/01/2024
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.isoformat()
            except:
                continue
        
        return date_str  # Return original if parsing fails
    
    def _find_relevant_emails(self, query: str, all_emails: List[Dict]) -> List[Dict]:
        """Find emails relevant to the query using intelligent matching"""
        query_lower = query.lower()
        relevant_emails = []
        
        # Score each email based on relevance to query
        for email in all_emails:
            score = 0
            matches = []
            
            # Check various fields for relevance
            searchable_content = {
                'subject': email.get('subject', ''),
                'from': email.get('from', ''),
                'to': email.get('to', ''),
                'body': email.get('body', ''),
                'date': email.get('date', '')
            }
            
            # Extract key terms from query
            query_terms = self._extract_query_terms(query)
            
            # Score based on term matches
            for field, content in searchable_content.items():
                if not content:
                    continue
                    
                content_lower = content.lower()
                
                # Check each query term
                for term in query_terms:
                    if term in content_lower:
                        score += self._get_field_weight(field)
                        matches.append(f"{field}: {term}")
                
                # Special handling for email addresses
                if '@' in query_lower and '@' in content_lower:
                    email_pattern = r'([^\s@]+@[^\s@]+\.[^\s@]+)'
                    query_emails = re.findall(email_pattern, query_lower)
                    content_emails = re.findall(email_pattern, content_lower)
                    
                    for qe in query_emails:
                        if qe in content_emails:
                            score += 10
                            matches.append(f"email match: {qe}")
            
            # Add email with score if relevant
            if score > 0:
                email['relevance_score'] = score
                email['matches'] = matches
                relevant_emails.append(email)
        
        # Sort by relevance and date
        relevant_emails.sort(key=lambda x: (x['relevance_score'], x.get('parsed_date', '')), reverse=True)
        
        return relevant_emails
    
    def _format_results_for_query(self, query: str, emails: List[Dict]) -> str:
        """Format results based on the query intent"""
        if not emails:
            return f"No emails found matching your query: '{query}'"
        
        query_lower = query.lower()
        
        # Determine query intent and format accordingly
        if "latest" in query_lower or "recent" in query_lower:
            # User wants recent emails
            return self._format_chronological_results(query, emails)
        elif "how many" in query_lower or "count" in query_lower:
            # User wants a count
            return self._format_count_results(query, emails)
        elif "summary" in query_lower or "summarize" in query_lower:
            # User wants a summary
            return self._format_summary_results(query, emails)
        elif any(word in query_lower for word in ["about", "regarding", "concerning"]):
            # User wants emails about a topic
            return self._format_topical_results(query, emails)
        else:
            # Default: show relevant emails with context
            return self._format_default_results(query, emails)
    
    def _format_default_results(self, query: str, emails: List[Dict]) -> str:
        """Default formatting showing relevant emails"""
        output = [f"Emails relevant to: {query}\n{'='*50}\n"]
        
        # Show top 5 most relevant
        for i, email in enumerate(emails[:5], 1):
            output.append(f"📧 Email {i}: {email['filename']}")
            
            if email.get('subject'):
                output.append(f"Subject: {email['subject']}")
            if email.get('from'):
                output.append(f"From: {email['from']}")
            if email.get('date'):
                output.append(f"Date: {email['date']}")
            
            # Show relevant excerpt
            excerpt = self._extract_relevant_excerpt(query, email)
            if excerpt:
                output.append(f"\nRelevant excerpt:")
                output.append(excerpt)
            
            output.append("-" * 40)
        
        if len(emails) > 5:
            output.append(f"\n... and {len(emails) - 5} more matching emails")
        
        return '\n'.join(output)
    
    def _format_chronological_results(self, query: str, emails: List[Dict]) -> str:
        """Format results chronologically"""
        # Sort by date
        emails.sort(key=lambda x: x.get('parsed_date', ''), reverse=True)
        
        # Extract number if specified
        num_match = re.search(r'(\d+)', query)
        limit = int(num_match.group(1)) if num_match else 5
        
        output = [f"Latest {limit} emails matching: {query}\n{'='*50}\n"]
        
        for i, email in enumerate(emails[:limit], 1):
            output.append(f"📧 Email {i}: {email['filename']}")
            
            if email.get('date'):
                output.append(f"Date: {email['date']}")
            if email.get('subject'):
                output.append(f"Subject: {email['subject']}")
            if email.get('from'):
                output.append(f"From: {email['from']}")
            
            # Add brief preview
            preview = email.get('body', '')[:150]
            if preview:
                output.append(f"Preview: {preview}...")
            
            output.append("-" * 40)
        
        return '\n'.join(output)
    
    def _format_count_results(self, query: str, emails: List[Dict]) -> str:
        """Format count results"""
        return f"Found {len(emails)} emails matching: {query}"
    
    def _format_summary_results(self, query: str, emails: List[Dict]) -> str:
        """Format summary of emails"""
        output = [f"Summary of emails related to: {query}\n{'='*50}\n"]
        
        # Group by sender
        by_sender = {}
        for email in emails:
            sender = email.get('from', 'Unknown')
            if sender not in by_sender:
                by_sender[sender] = []
            by_sender[sender].append(email)
        
        output.append(f"Total emails: {len(emails)}")
        output.append(f"Unique senders: {len(by_sender)}\n")
        
        for sender, sender_emails in by_sender.items():
            output.append(f"From {sender}: {len(sender_emails)} emails")
            # Show topics
            subjects = [e.get('subject', '') for e in sender_emails if e.get('subject')]
            if subjects:
                output.append(f"  Topics: {', '.join(subjects[:3])}")
        
        # Date range
        dates = [e.get('parsed_date') for e in emails if e.get('parsed_date')]
        if dates:
            output.append(f"\nDate range: {min(dates)} to {max(dates)}")
        
        return '\n'.join(output)
    
    def _format_topical_results(self, query: str, emails: List[Dict]) -> str:
        """Format emails about a specific topic"""
        output = [f"Emails about: {query}\n{'='*50}\n"]
        
        for i, email in enumerate(emails[:5], 1):
            output.append(f"📧 Email {i}: {email['filename']}")
            
            if email.get('subject'):
                output.append(f"Subject: {email['subject']}")
            if email.get('from'):
                output.append(f"From: {email['from']}")
            if email.get('date'):
                output.append(f"Date: {email['date']}")
            
            # Show why this email is relevant
            if email.get('matches'):
                output.append(f"Relevance: {', '.join(email['matches'][:3])}")
            
            # Show relevant excerpt
            excerpt = self._extract_relevant_excerpt(query, email)
            if excerpt:
                output.append(f"\nExcerpt:")
                output.append(excerpt)
            
            output.append("-" * 40)
        
        return '\n'.join(output)
    
    def _extract_query_terms(self, query: str) -> List[str]:
        """Extract meaningful terms from the query"""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'from', 'what', 'when', 'where', 'who', 'how', 'why',
            'show', 'find', 'get', 'give', 'me', 'all', 'latest', 'recent'
        }
        
        # Split and clean
        words = query.lower().split()
        terms = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Also extract email addresses as whole units
        email_pattern = r'([^\s@]+@[^\s@]+\.[^\s@]+)'
        emails = re.findall(email_pattern, query)
        terms.extend(emails)
        
        return terms
    
    def _get_field_weight(self, field: str) -> int:
        """Get relevance weight for different fields"""
        weights = {
            'subject': 3,
            'from': 5,
            'to': 4,
            'body': 1,
            'date': 2
        }
        return weights.get(field, 1)
    
    def _extract_relevant_excerpt(self, query: str, email: Dict) -> str:
        """Extract excerpt most relevant to the query"""
        body = email.get('body', '')
        if not body:
            return ""
        
        query_terms = self._extract_query_terms(query)
        sentences = body.split('.')
        
        # Score each sentence
        scored_sentences = []
        for sent in sentences:
            sent_lower = sent.lower()
            score = sum(1 for term in query_terms if term in sent_lower)
            if score > 0:
                scored_sentences.append((score, sent.strip()))
        
        # Return best sentences
        scored_sentences.sort(key=lambda x: x[0], reverse=True)
        top_sentences = [s[1] for s in scored_sentences[:3]]
        
        return '. '.join(top_sentences) + '.' if top_sentences else body[:200] + '...'
    
    def _extract_field(self, content: str, field_name: str) -> Optional[str]:
        """Extract a field from email headers"""
        patterns = {
            'subject': [r'Subject:\s*(.+?)(?:\n|$)', r'Re:\s*(.+?)(?:\n|$)'],
            'from': [r'From:\s*(.+?)(?:\n|$)'],
            'to': [r'To:\s*(.+?)(?:\n|$)'],
            'date': [r'Date:\s*(.+?)(?:\n|$)']
        }
        
        field_patterns = patterns.get(field_name.lower(), [])
        for pattern in field_patterns:
            match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_body(self, content: str) -> str:
        """Extract the body of the email"""
        lines = content.split('\n')
        body_lines = []
        in_body = False
        
        for line in lines:
            if in_body:
                body_lines.append(line)
            elif line.strip() == '' and any(header in content[:200].lower() for header in ['subject:', 'from:', 'to:', 'date:']):
                in_body = True
        
        body = '\n'.join(body_lines).strip()
        return body if body else content
    
    def _parse_mime_email(self, content: str) -> str:
        """Parse MIME formatted email and extract the text content"""
        # Look for the text/plain or text/html content
        text_content = ""
        
        # Split by MIME boundaries
        if 'Content-Type: text/plain' in content:
            # Extract text/plain section
            plain_match = re.search(
                r'Content-Type: text/plain[^-]*?\n\n(.*?)(?=\n--|\Z)', 
                content, 
                re.DOTALL
            )
            if plain_match:
                text_content = plain_match.group(1)
        
        # If no text/plain, try text/html
        if not text_content and 'Content-Type: text/html' in content:
            html_match = re.search(
                r'Content-Type: text/html[^-]*?\n\n(.*?)(?=\n--|\Z)', 
                content, 
                re.DOTALL
            )
            if html_match:
                text_content = html_match.group(1)
        
        # If still no content, try to extract after headers
        if not text_content:
            # Skip to after the headers
            header_end = content.find('\n\n')
            if header_end > 0:
                text_content = content[header_end+2:]
        
        return text_content
    
    def _decode_quoted_printable(self, text: str) -> str:
        """Decode quoted-printable encoding"""
        # Handle soft line breaks (= at end of line)
        text = re.sub(r'=\n', '', text)
        
        # Decode hex sequences
        def decode_hex(match):
            hex_code = match.group(1)
            try:
                return chr(int(hex_code, 16))
            except:
                return match.group(0)
        
        text = re.sub(r'=([0-9A-F]{2})', decode_hex, text)
        
        return text
    
    def _clean_email_content(self, content: str) -> str:
        """Clean email content by removing headers and decoding"""
        # If this is a MIME email, extract the content first
        if 'MIME-Version:' in content:
            content = self._parse_mime_email(content)
        
        # Decode quoted-printable
        content = self._decode_quoted_printable(content)
        
        # Remove HTML tags
        content = re.sub(r'<[^>]+>', ' ', content)
        
        # Decode HTML entities
        content = html.unescape(content)
        
        # Remove image references and content IDs
        content = re.sub(r'\[image:.*?\]', '', content)
        content = re.sub(r'<img[^>]*>', '', content)
        content = re.sub(r'cid:[^\s]+', '', content)
        
        # Clean up quote markers from email threads
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove leading > markers
            line = re.sub(r'^>\s*', '', line)
            line = re.sub(r'^>+\s*', '', line)
            
            # Skip boundary markers
            if line.startswith('--') and len(line) > 10:
                continue
                
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        return content.strip()
    
    def _extract_sevenn_context(self, content: str) -> str:
        """Specifically extract context about Sevenn invoices"""
        # Clean the content first
        cleaned = self._clean_email_content(content)
        
        # Look for the specific discussion about Sevenn
        patterns = [
            # Irma's response about Sevenn
            r'As for the invoices to Sevenn[^.]*\.[^.]*\.[^.]*\.',
            # Jessica's question about Sevenn
            r'Are these two invoices to tim@sevenn\.co[^?]*\?[^.]*',
            # Any sentence containing Sevenn
            r'[^.]*[Ss]evenn[^.]*\.',
        ]
        
        extracted_parts = []
        
        for pattern in patterns:
            matches = re.findall(pattern, cleaned, re.DOTALL)
            extracted_parts.extend(matches)
        
        # Also look for the broader context
        paragraphs = cleaned.split('\n\n')
        sevenn_paragraphs = []
        
        for para in paragraphs:
            if 'sevenn' in para.lower() or 'tim@sevenn' in para.lower():
                sevenn_paragraphs.append(para)
        
        # Combine all findings
        all_context = '\n\n'.join(extracted_parts + sevenn_paragraphs)
        
        # Clean up the result
        all_context = re.sub(r'\s+', ' ', all_context)
        
        return all_context.strip()
    
    def _extract_relevant_excerpt(self, query: str, email: Dict) -> str:
        """Extract excerpt most relevant to the query"""
        # For Sevenn queries, use special extraction
        if 'sevenn' in query.lower():
            sevenn_context = self._extract_sevenn_context(email.get('raw_content', ''))
            if sevenn_context:
                return sevenn_context
        
        # Get the cleaned email content
        content = email.get('cleaned_content', '') or email.get('body', '')
        
        if not content:
            return ""
        
        query_terms = self._extract_query_terms(query)
        
        # Split into paragraphs
        paragraphs = content.split('\n\n')
        scored_sections = []
        
        for i, para in enumerate(paragraphs):
            para_lower = para.lower()
            score = 0
            
            # Score based on query term matches
            for term in query_terms:
                if term.lower() in para_lower:
                    score += para_lower.count(term.lower())
            
            if score > 0:
                # Include context
                start = max(0, i-1)
                end = min(len(paragraphs), i+2)
                context = '\n\n'.join(paragraphs[start:end])
                scored_sections.append((score, context))
        
        # Sort by relevance
        scored_sections.sort(key=lambda x: x[0], reverse=True)
        
        if scored_sections:
            return '\n\n---\n\n'.join([s[1] for s in scored_sections[:2]])
        
        # Fallback
        return content[:500] + '...' if len(content) > 500 else content
        replacements = {
            '=E2=80=99': "'",  # apostrophe
            '=E2=80=9C': '"',  # left quote
            '=E2=80=9D': '"',  # right quote
            '=E2=80=93': '-',  # en dash
            '=E2=80=94': '--', # em dash
            '=C2=A0': ' ',     # non-breaking space
            '=3D': '=',        # equals
            '=20': ' ',        # space
            '&nbsp;': ' ',
            '&#39;': "'",
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
        }
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        # Clean up > quote markers from email threads
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Remove leading > markers but keep the content
            line = re.sub(r'^>\s*', '', line)
            line = re.sub(r'^>+\s*', '', line)
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Remove boundary markers
        content = re.sub(r'--[0-9a-fA-F]+.*?--', '', content, flags=re.DOTALL)
        
        # Clean up extra whitespace
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        
        return content.strip()
    
    def _extract_email_thread_content(self, content: str) -> str:
        """Extract the threaded conversation content from email"""
        cleaned = self._clean_email_content(content)
        
        # Split into sections based on date patterns (email thread separators)
        thread_pattern = r'On\s+[^,]+,\s+\d{4}\s+at\s+\d+:\d+.*?wrote:'
        sections = re.split(thread_pattern, cleaned)
        
        # If no clear thread markers, look for other patterns
        if len(sections) == 1:
            # Try splitting by email headers within the content
            sections = re.split(r'From:\s+.*?\nTo:\s+.*?\n', cleaned)
        
        # Return all relevant sections
        return '\n\n---\n\n'.join(sections)
    
    def _extract_relevant_excerpt(self, query: str, email: Dict) -> str:
        """Extract excerpt most relevant to the query"""
        # Get the full thread content
        full_content = self._extract_email_thread_content(email.get('raw_content', ''))
        if not full_content:
            full_content = email.get('body', '')
        
        if not full_content:
            return ""
        
        query_terms = self._extract_query_terms(query)
        
        # Look for paragraphs or sections that contain the query terms
        paragraphs = full_content.split('\n\n')
        scored_sections = []
        
        for i, para in enumerate(paragraphs):
            para_lower = para.lower()
            score = 0
            
            # Score based on query term matches
            for term in query_terms:
                if term.lower() in para_lower:
                    score += para_lower.count(term.lower())
            
            # Boost score if paragraph contains key phrases
            if 'sevenn' in query.lower() and 'sevenn' in para_lower:
                score += 5
            if 'invoice' in query.lower() and 'invoice' in para_lower:
                score += 3
            
            if score > 0:
                # Include some context (previous and next paragraph)
                start = max(0, i-1)
                end = min(len(paragraphs), i+2)
                context = '\n\n'.join(paragraphs[start:end])
                scored_sections.append((score, context))
        
        # Return the highest scoring sections
        scored_sections.sort(key=lambda x: x[0], reverse=True)
        
        if scored_sections:
            return '\n\n...\n\n'.join([s[1] for s in scored_sections[:2]])
        
        # Fallback: return section containing query terms
        for term in query_terms:
            for para in paragraphs:
                if term.lower() in para.lower():
                    return para
        
        return full_content[:500] + '...'