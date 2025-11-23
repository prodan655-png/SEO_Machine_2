"""
Sitemap Parser Module.
Extracts URLs from XML sitemaps for internal linking analysis.
"""

import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
from urllib.parse import urlparse
from logger import setup_logger

logger = setup_logger(__name__)

class SitemapParser:
    """Parses XML sitemaps to extract URLs."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; SEOAnalyzer/1.0; +http://example.com)'
        }
    
    def parse_sitemap(self, url: str) -> List[str]:
        """
        Parse a sitemap URL and return a list of page URLs.
        Handles sitemap indexes recursively.
        """
        try:
            logger.info(f"Fetching sitemap: {url}")
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Parse XML
            root = ET.fromstring(response.content)
            
            # Check if it's a sitemap index
            if 'sitemapindex' in root.tag:
                return self._handle_sitemap_index(root)
            else:
                return self._handle_urlset(root)
                
        except Exception as e:
            logger.error(f"Error parsing sitemap {url}: {str(e)}")
            return []

    def _handle_sitemap_index(self, root: ET.Element) -> List[str]:
        """Handle sitemap index (recursive parsing)."""
        urls = []
        # Namespaces are annoying in XML, usually it's default
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        for sitemap in root.findall('ns:sitemap', ns):
            loc = sitemap.find('ns:loc', ns)
            if loc is not None and loc.text:
                urls.extend(self.parse_sitemap(loc.text))
                
        return urls

    def _handle_urlset(self, root: ET.Element) -> List[str]:
        """Handle standard urlset."""
        urls = []
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        
        for url in root.findall('ns:url', ns):
            loc = url.find('ns:loc', ns)
            if loc is not None and loc.text:
                urls.append(loc.text)
                
        return urls

def parse_sitemap(url: str) -> List[str]:
    """Convenience wrapper."""
    parser = SitemapParser()
    return parser.parse_sitemap(url)
