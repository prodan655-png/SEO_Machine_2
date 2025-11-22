"""
Unit tests for content_extractor module.
"""

import pytest
from modules.content_extractor import (
    extract_main_content,
    detect_language,
    ContentExtractionError
)


def test_extract_main_content_basic():
    """Test basic content extraction."""
    html = """
    <html lang="en">
    <head><title>Test Page</title></head>
    <body>
        <header><nav>Navigation</nav></header>
        <main>
            <h1>Main Title</h1>
            <p>First paragraph with content.</p>
            <h2>Section One</h2>
            <p>More content here.</p>
            <h3>Subsection</h3>
            <p>Even more content.</p>
            <img src="test.jpg" alt="Test">
        </main>
        <footer>Footer</footer>
    </body>
    </html>
    """
    
    result = extract_main_content(html, "http://example.com")
    
    assert result['status'] == 'valid'
    assert result['word_count'] > 0
    assert len(result['headings']) == 3
    assert result['image_count'] == 1
    assert 'Main Title' in result['title']


def test_extract_main_content_weak():
    """Test weak content detection (< 200 words)."""
    html = """
    <html>
    <body>
        <p>Short content.</p>
    </body>
    </html>
    """
    
    result = extract_main_content(html, "http://example.com")
    
    assert result['status'] == 'weak'
    assert result['word_count'] < 200


def test_detect_language():
    """Test language detection."""
    # HTML with lang attribute
    html_en = '<html lang="en-US"><body>Content</body></html>'
    assert detect_language(html_en) == 'en'
    
    # HTML with uk lang
    html_uk = '<html lang="uk"><body>Контент</body></html>'
    assert detect_language(html_uk) == 'uk'
    
    # No language specified
    html_none = '<html><body>Content</body></html>'
    assert detect_language(html_none) is None


def test_extract_headings():
    """Test heading extraction."""
    html = """
    <html>
    <body>
        <h1>Title</h1>
        <h2>Section 1</h2>
        <h2>Section 2</h2>
        <h3>Subsection</h3>
    </body>
    </html>
    """
    
    result = extract_main_content(html, "http://example.com")
    
    headings = result['headings']
    assert len(headings) == 4
    assert headings[0]['level'] == 'h1'
    assert headings[0]['text'] == 'Title'
    assert headings[1]['level'] == 'h2'


def test_remove_unwanted_elements():
    """Test that scripts/styles are removed."""
    html = """
    <html>
    <body>
        <script>alert('test');</script>
        <style>.class { color: red; }</style>
        <p>Actual content</p>
        <nav>Navigation</nav>
    </body>
    </html>
    """
    
    result = extract_main_content(html, "http://example.com")
    
    text = result['main_text'].lower()
    assert 'alert' not in text
    assert 'color' not in text
    assert 'actual content' in text
