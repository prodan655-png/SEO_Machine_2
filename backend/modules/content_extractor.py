"""
Content Extractor Module.
Scrapes and extracts content from competitor URLs.
"""

from typing import Dict, List, Any, Optional
import requests
from bs4 import BeautifulSoup
import re
from logger import setup_logger
from config import get_config

logger = setup_logger(__name__)


class ContentExtractionError(Exception):
    """Raised when content extraction fails."""
    pass


def fetch_page_content(url: str, timeout: int = 30) -> str:
    """
    Fetch HTML content from URL.
    
    Args:
        url: URL to fetch
        timeout: Request timeout in seconds
    
    Returns:
        HTML content as string
    
    Raises:
        ContentExtractionError: If request fails
    """
    user_agents = get_config('content_extraction.user_agents', [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    ])
    
    headers = {
        'User-Agent': user_agents[0],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    
    max_redirects = get_config('content_extraction.max_redirects', 5)
    
    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            allow_redirects=True,
            max_redirects=max_redirects
        )
        response.raise_for_status()
        return response.text
    
    except requests.exceptions.Timeout:
        raise ContentExtractionError(f"Request timeout for {url}")
    except requests.exceptions.TooManyRedirects:
        raise ContentExtractionError(f"Too many redirects for {url}")
    except requests.exceptions.RequestException as e:
        raise ContentExtractionError(f"Request failed for {url}: {str(e)}")


def detect_language(html: str) -> Optional[str]:
    """
    Detect page language from HTML.
    
    Args:
        html: HTML content
    
    Returns:
        Language code (e.g., 'en', 'uk') or None
    """
    soup = BeautifulSoup(html, 'lxml')
    
    # Try html lang attribute
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        lang = html_tag.get('lang').lower()
        return lang.split('-')[0]  # 'en-US' -> 'en'
    
    # Try meta tags
    meta_lang = soup.find('meta', attrs={'http-equiv': 'content-language'})
    if meta_lang and meta_lang.get('content'):
        lang = meta_lang.get('content').lower()
        return lang.split('-')[0]
    
    return None


def extract_main_content(html: str, url: str) -> Dict[str, Any]:
    """
    Extract main content from HTML page.
    
    Args:
        html: HTML content
        url: Source URL
    
    Returns:
        Dict with extracted content data
    """
    soup = BeautifulSoup(html, 'lxml')
    
    # Remove unwanted elements
    for element in soup(['script', 'style', 'nav', 'header', 'footer', 
                        'aside', 'iframe', 'noscript']):
        element.decompose()
    
    # Try to find main content area
    main_content = (
        soup.find('main') or 
        soup.find('article') or
        soup.find('div', class_=re.compile(r'content|main|post|article', re.I)) or
        soup.find('body')
    )
    
    if not main_content:
        logger.warning(f"No main content area found for {url}")
        main_content = soup.find('body') or soup
    
    # Extract text
    main_text = main_content.get_text(separator=' ', strip=True)
    main_text = re.sub(r'\s+', ' ', main_text)  # Normalize whitespace
    
    # Extract headings
    headings = []
    for tag in ['h1', 'h2', 'h3']:
        for heading in main_content.find_all(tag):
            text = heading.get_text(strip=True)
            if text:
                headings.append({
                    'level': tag,
                    'text': text
                })
    
    # Count metrics
    words = main_text.split()
    word_count = len(words)
    
    paragraphs = main_content.find_all('p')
    paragraph_count = len([p for p in paragraphs if p.get_text(strip=True)])
    
    images = main_content.find_all('img')
    image_count = len(images)
    
    # Determine status
    min_word_count = get_config('content_extraction.min_word_count', 200)
    
    if word_count < min_word_count:
        status = "weak"
    else:
        status = "valid"
    
    # Extract title
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else ""
    
    detected_lang = detect_language(html)
    
    logger.info(f"Extracted content from {url}: {word_count} words, {len(headings)} headings, status={status}")
    
    return {
        'url': url,
        'title': title,
        'main_text': main_text,
        'detected_language': detected_lang,
        'headings': headings,
        'word_count': word_count,
        'paragraph_count': paragraph_count,
        'image_count': image_count,
        'status': status,
        'error': None
    }


async def batch_extract_competitors(urls: List[str]) -> List[Dict[str, Any]]:
    """
    Extract content from multiple URLs in parallel.
    
    Args:
        urls: List of URLs to extract
    
    Returns:
        List of extraction results
    """
    import asyncio
    import aiohttp
    from concurrent.futures import ThreadPoolExecutor
    
    results = []
    timeout = get_config('content_extraction.request_timeout', 30)
    
    def extract_single(url: str) -> Dict[str, Any]:
        """Extract content from single URL (synchronous)."""
        try:
            html = fetch_page_content(url, timeout)
            return extract_main_content(html, url)
        except ContentExtractionError as e:
            logger.error(f"Failed to extract {url}: {str(e)}")
            return {
                'url': url,
                'title': '',
                'main_text': '',
                'detected_language': None,
                'headings': [],
                'word_count': 0,
                'paragraph_count': 0,
                'image_count': 0,
                'status': 'failed',
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {str(e)}")
            return {
                'url': url,
                'status': 'failed',
                'error': f"Unexpected error: {str(e)}"
            }
    
    # Use ThreadPoolExecutor for parallel extraction
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(extract_single, url) for url in urls]
        results = [future.result() for future in futures]
    
    valid_count = len([r for r in results if r['status'] == 'valid'])
    logger.info(f"Batch extraction complete: {valid_count}/{len(results)} valid")
    
    return results


if __name__ == "__main__":
    # Test with a simple example
    test_html = """
    <html lang="en">
    <head><title>Test Page</title></head>
    <body>
        <header><nav>Navigation</nav></header>
        <main>
            <h1>Main Title</h1>
            <p>First paragraph with some content.</p>
            <h2>Section 1</h2>
            <p>More content here.</p>
            <h2>Section 2</h2>
            <p>Even more content.</p>
            <img src="test.jpg" alt="Test">
        </main>
        <footer>Footer content</footer>
    </body>
    </html>
    """
    
    result = extract_main_content(test_html, "http://example.com")
    print(f"Title: {result['title']}")
    print(f"Word count: {result['word_count']}")
    print(f"Headings: {len(result['headings'])}")
    print(f"Status: {result['status']}")
