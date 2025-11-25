"""
Golden Test Suite for Scoring System
Tests scoring algorithm against known articles with expected scores
"""

import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.content_scorer import compute_content_score
from modules.scoring_constants import SCORING_VERSION


# Test data: known articles with expected score ranges
GUIDELINES = {
    'word_count': {'min': 1000, 'max': 2000, 'median': 1500},
    'headings': {'min': 5, 'max': 10, 'median': 7},
    'images': {'min': 2, 'max': 5, 'median': 3}
}

TERMS = [
    {'term': 'SEO', 'term_normalized': 'seo', 'min_recommended': 8, 'max_recommended': 15},
    {'term': 'content', 'term_normalized': 'content', 'min_recommended': 10, 'max_recommended': 20},
    {'term': 'optimization', 'term_normalized': 'optimization', 'min_recommended': 5, 'max_recommended': 10},
    {'term': 'keywords', 'term_normalized': 'keywords', 'min_recommended': 6, 'max_recommended': 12},
    {'term': 'search engine', 'term_normalized': 'search engine', 'min_recommended': 4, 'max_recommended': 8}
]


def test_version_tracking():
    """Verify scoring version is returned."""
    article = "<h1>Test</h1><p>Content</p>"
    result = compute_content_score(article, GUIDELINES, TERMS, 'html')
    
    assert 'scoring_version' in result
    assert result['scoring_version'] == SCORING_VERSION


def test_golden_perfect_article():
    """Test article with perfect term coverage and structure."""
    article = f"""
    <h1>Complete Guide to SEO Content Optimization</h1>
    
    <p>SEO content optimization is essential for search engine visibility. This guide covers 
    SEO best practices, content strategies, and optimization techniques for better keywords ranking.</p>
    
    <h2>Understanding SEO Fundamentals</h2>
    <p>Search engine optimization impacts how search engines rank your content. Good SEO practices 
    include keyword research, content quality, and optimization for both users and search engines.</p>
    
    <h2>Content Creation Strategies</h2>
    <p>Creating quality content requires understanding your audience. SEO content should include 
    relevant keywords naturally, provide value, and answer user questions.</p>
    <img src="chart1.jpg" alt="SEO metrics">
    
    <h2>Keyword Research and Implementation</h2>
    <p>Effective keywords research identifies terms your audience searches for. Implement keywords 
    strategically in content, headers, and meta tags. Search engine algorithms value natural keyword usage.</p>
    <img src="chart2.jpg" alt="Keyword analysis">
    
    <h2>On-Page Optimization Techniques</h2>
    <p>On-page SEO optimization includes title tags, meta descriptions, headers, and content structure. 
    Proper optimization helps search engines understand your content better.</p>
    
    <h2>Measuring SEO Success</h2>
    <p>Track SEO performance through analytics. Monitor keywords rankings, organic traffic, and 
    content engagement. Regular optimization based on data improves search engine results.</p>
    <img src="chart3.jpg" alt="Analytics">
    
    <h2>Advanced Content Strategies</h2>
    <p>Advanced SEO techniques include semantic keywords, content clusters, and search intent optimization. 
    Quality content with proper optimization ranks higher in search results.</p>
    
    <h2>Common SEO Mistakes to Avoid</h2>
    <p>Avoid keyword stuffing, thin content, and poor optimization practices. Focus on creating valuable 
    content that serves users while following SEO best practices.</p>
    <img src="chart4.jpg" alt="Best practices">
    """ + " ".join(["Additional filler content word"] * 200)  # Pad to ~1500 words
    
    result = compute_content_score(article, GUIDELINES, TERMS, 'html')
    
    # Perfect article should score 85-100
    assert result['total_score'] >= 85, f"Perfect article scored {result['total_score']}, expected >= 85"
    assert result['breakdown']['term_coverage']['score'] >= 50  # Strong term coverage
    assert result['breakdown']['headings']['score'] >= 15       # Good headings


def test_golden_missing_terms():
    """Test article with poor term coverage."""
    article = """
    <h1>General Article</h1>
    
    <h2>Introduction</h2>
    <p>This is a general article about topics. It contains information but lacks specific terminology.</p>
    
    <h2>Main Content</h2>
    <p>The discussion covers various aspects. Information is presented in a structured format.</p>
    <img src="image.jpg">
    
    <h2>Details</h2>
    <p>More details are provided here. The article continues with additional information.</p>
    
    <h2>Analysis</h2>
    <p>Analysis of the subject matter follows. Various points are considered.</p>
    <img src="image2.jpg">
    
    <h2>Conclusion</h2>
    <p>Final thoughts summarize the discussion. Key points are reiterated.</p>
    """ + " ".join(["filler word"] * 300)  # Pad to ~1500 words
    
    result = compute_content_score(article, GUIDELINES, TERMS, 'html')
    
    # Missing terms should score 50-70
    assert 50 <= result['total_score'] < 75, f"Missing terms scored {result['total_score']}, expected 50-75"
    assert result['breakdown']['term_coverage']['score'] < 40  # Poor term coverage


def test_golden_over_optimized():
    """Test article with keyword stuffing."""
    # Repeat terms excessively
    article = f"""
    <h1>SEO SEO SEO Content Optimization SEO</h1>
    
    <h2>SEO Content SEO Keywords SEO</h2>
    <p>SEO content optimization SEO keywords SEO search engine SEO optimization SEO.
    SEO content SEO keywords SEO search engine SEO optimization SEO content SEO.</p>
    
    <h2>More SEO Content Keywords Optimization</h2>
    <p>SEO content optimization keywords search engine optimization content SEO keywords.
    Search engine optimization content keywords SEO optimization search engine content.</p>
    <img src="img.jpg">
    
    <h2>Keywords SEO Optimization Content</h2>
    <p>Content keywords SEO optimization search engine keywords content optimization SEO.
    Keywords content search engine SEO optimization keywords content search engine.</p>
    <img src="img2.jpg">
    """ + " SEO content optimization keywords search engine " * 100  # Excessive repetition
    
    result = compute_content_score(article, GUIDELINES, TERMS, 'html')
    
    # Over-optimization should score 40-65
    assert 40 <= result['total_score'] < 70, f"Over-optimized scored {result['total_score']}, expected 40-70"
    assert result['breakdown']['term_coverage']['score'] < 50  # Penalized for stuffing


def test_golden_missing_headings():
    """Test article with insufficient headings."""
    article = f"""
    <h1>SEO Content Optimization Guide</h1>
    
    <p>SEO content optimization is crucial for search engine visibility. This guide covers 
    SEO practices, content strategies, optimization techniques, and keywords implementation.
    Search engine optimization involves creating quality content with relevant keywords.
    Content optimization helps search engines understand your material better.
    Keywords should be used naturally throughout the content for best SEO results.
    Search engine algorithms favor well-optimized content with proper keyword usage.
    Optimization techniques include on-page SEO, content structure, and keywords research.
    SEO content should provide value while incorporating important keywords naturally.
    Search engine optimization requires understanding both technical and content aspects.
    Content optimization involves balancing keywords with readability and user experience.</p>
    
    <p>Continuing with SEO practices, content creators must focus on optimization quality.
    Keywords placement matters for search engine rankings and content discoverability.
    SEO optimization requires consistent effort and attention to search engine guidelines.
    Content should incorporate keywords while maintaining natural flow and readability.
    Search engine optimization evolves, requiring ongoing content optimization efforts.</p>
    
    <img src="chart.jpg" alt="SEO">
    <img src="chart2.jpg" alt="Keywords">
    """ + " ".join([f"SEO content optimization keywords search engine filler {i}" for i in range(200)])
    
    result = compute_content_score(article, GUIDELINES, TERMS, 'html')
    
    # Missing headings should score 60-80
    assert 60 <= result['total_score'] < 80, f"Missing headings scored {result['total_score']}, expected 60-80"
    assert result['breakdown']['headings']['score'] < 15  # Penalized for few headings


def test_golden_short_content():
    """Test article that's too short."""
    article = """
    <h1>SEO Guide</h1>
    
    <h2>Introduction to SEO</h2>
    <p>SEO content optimization uses keywords for search engine visibility. 
    Content should include relevant keywords and proper optimization techniques.</p>
    
    <h2>Keywords Strategy</h2>
    <p>Search engine optimization requires keyword research. Implement keywords 
    in content for better search engine rankings and optimization results.</p>
    
    <h2>Best Practices</h2>
    <p>SEO best practices include quality content, keywords usage, and optimization.
    Search engines favor well-optimized content with natural keyword implementation.</p>
    
    <img src="img.jpg" alt="SEO chart">
    """
    
    result = compute_content_score(article, GUIDELINES, TERMS, 'html')
    
    # Short content should score 30-55
    assert 30 <= result['total_score'] < 60, f"Short content scored {result['total_score']}, expected 30-60"
    assert result['breakdown']['structure']['score'] < 15  # Penalized for length


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, '-v'])
