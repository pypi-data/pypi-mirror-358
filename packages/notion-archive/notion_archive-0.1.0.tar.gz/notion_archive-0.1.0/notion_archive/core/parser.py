"""
Notion export parser for extracting content from HTML files.
"""

import os
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from bs4 import BeautifulSoup
from dataclasses import dataclass
from datetime import datetime


@dataclass
class NotionDocument:
    """Represents a parsed Notion document."""
    
    id: str
    title: str
    content: str
    plain_text: str
    url_path: str
    created_by: Optional[str] = None
    created_time: Optional[datetime] = None
    last_edited_by: Optional[str] = None
    last_edited_time: Optional[datetime] = None
    tags: List[str] = None
    workspace: str = ""
    breadcrumb: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.breadcrumb is None:
            self.breadcrumb = []


class NotionExportParser:
    """Parser for Notion HTML exports."""
    
    def __init__(self, export_path: str):
        self.export_path = Path(export_path)
        self.documents: List[NotionDocument] = []
        
    def parse_export(self) -> List[NotionDocument]:
        """Parse all HTML files in the Notion export."""
        
        # Find all HTML files recursively
        html_files = list(self.export_path.rglob("*.html"))
        
        # Skip the main index.html file
        html_files = [f for f in html_files if f.name != "index.html"]
        
        for html_file in html_files:
            try:
                doc = self._parse_html_file(html_file)
                if doc:
                    self.documents.append(doc)
            except Exception as e:
                print(f"Error parsing {html_file}: {e}")
                continue
                
        return self.documents
    
    def _parse_html_file(self, file_path: Path) -> Optional[NotionDocument]:
        """Parse a single HTML file into a NotionDocument."""
        
        # Safety check: file size limit (10MB)
        if file_path.stat().st_size > 10 * 1024 * 1024:
            print(f"Warning: Skipping large file {file_path.name} ({file_path.stat().st_size / 1024 / 1024:.1f}MB)")
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract title
        title_elem = soup.find('h1', class_='page-title')
        title = title_elem.get_text().strip() if title_elem else file_path.stem
        
        # Extract document ID from the article element
        article = soup.find('article')
        doc_id = article.get('id') if article else self._extract_id_from_filename(file_path.name)
        
        # Extract metadata from properties table
        metadata = self._extract_metadata(soup)
        
        # Extract main content
        page_body = soup.find('div', class_='page-body')
        if not page_body:
            return None
            
        # Clean and extract text content
        plain_text = self._extract_plain_text(page_body)
        html_content = str(page_body)
        
        # Determine workspace and breadcrumb from file path
        workspace, breadcrumb = self._extract_path_info(file_path)
        
        # Create relative URL path
        url_path = str(file_path.relative_to(self.export_path))
        
        return NotionDocument(
            id=doc_id,
            title=title,
            content=html_content,
            plain_text=plain_text,
            url_path=url_path,
            workspace=workspace,
            breadcrumb=breadcrumb,
            **metadata
        )
    
    def _extract_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract metadata from the properties table."""
        metadata = {}
        
        properties_table = soup.find('table', class_='properties')
        if not properties_table:
            return metadata
            
        for row in properties_table.find_all('tr'):
            cells = row.find_all(['th', 'td'])
            if len(cells) >= 2:
                key = cells[0].get_text().strip().lower().replace(' ', '_')
                value_cell = cells[1]
                
                if key == 'created_by' or key == 'last_edited_by':
                    user_elem = value_cell.find('span', class_='user')
                    metadata[key] = user_elem.get_text().strip() if user_elem else None
                    
                elif key == 'created_time' or key == 'last_edited_time':
                    time_elem = value_cell.find('time')
                    if time_elem:
                        time_str = time_elem.get_text().strip().replace('@', '').strip()
                        try:
                            metadata[key] = datetime.strptime(time_str, '%B %d, %Y %I:%M %p')
                        except ValueError:
                            metadata[key] = None
                            
                elif key == 'tags':
                    tags = []
                    for tag_elem in value_cell.find_all('span', class_='selected-value'):
                        tags.append(tag_elem.get_text().strip())
                    metadata[key] = tags
                    
        return metadata
    
    def _extract_plain_text(self, element) -> str:
        """Extract clean plain text from HTML element."""
        
        # Remove script and style elements
        for script in element(["script", "style"]):
            script.decompose()
            
        # Get text and clean it up
        text = element.get_text()
        
        # Replace multiple whitespace with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Remove extra newlines and spaces
        text = text.strip()
        
        return text
    
    def _extract_path_info(self, file_path: Path) -> Tuple[str, List[str]]:
        """Extract workspace and breadcrumb information from file path."""
        
        # Get relative path from export root
        rel_path = file_path.relative_to(self.export_path)
        parts = rel_path.parts[:-1]  # Exclude filename
        
        workspace = ""
        breadcrumb = []
        
        if parts:
            # First part is usually the main export folder
            if len(parts) > 1:
                workspace = self._clean_folder_name(parts[1])
                breadcrumb = [self._clean_folder_name(part) for part in parts[1:]]
            else:
                workspace = self._clean_folder_name(parts[0])
                breadcrumb = [workspace]
                
        return workspace, breadcrumb
    
    def _clean_folder_name(self, folder_name: str) -> str:
        """Clean folder names by removing Notion IDs and extra characters."""
        
        # Remove Notion ID patterns (32-character hex strings)
        name = re.sub(r'\s+[a-f0-9]{32}', '', folder_name)
        name = re.sub(r'^[a-f0-9]{32}\s+', '', name)
        name = re.sub(r'\s+[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', '', name)
        
        # Clean up extra spaces and special characters
        name = re.sub(r'\s+', ' ', name).strip()
        
        return name
    
    def _extract_id_from_filename(self, filename: str) -> str:
        """Extract Notion document ID from filename."""
        
        # Look for 32-character hex ID in filename
        match = re.search(r'([a-f0-9]{32})', filename)
        if match:
            return match.group(1)
            
        # Look for UUID format
        uuid_match = re.search(r'([a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12})', filename)
        if uuid_match:
            return uuid_match.group(1)
            
        # Fallback to filename without extension
        return filename.replace('.html', '')


def parse_notion_export(export_path: str) -> List[NotionDocument]:
    """Convenience function to parse a Notion export."""
    parser = NotionExportParser(export_path)
    return parser.parse_export()