"""
Unit tests for content_scorer module.
"""

import pytest
from modules.content_scorer import (
    parse_draft_content,
    compute_content_score,
    calculate_term_coverage_score,
    calculate_structure_score,
    calculate_headings_score
)


def test_parse_draft_html():
    """Test HTML draft parsing."""
    html = """
    <h1>Main Title</h1>
    <p>First paragraph.</p>
    <h2>Section</h2>
    <p>Second paragraph.</p>
    <img src="test.jpg">
    """
    
    result = parse_draft_content(html, 'html')
    
    assert result['word_count'] > 0
    assert result['has_h1'] is True
    assert result['h2_h3_count'] == 1
    assert result['image_count'] == 1


def test_no_terms_score():
    """Test score when no terms are used."""
    draft = "<p>Some random content without terms.</p>"
    guidelines = {
        'word_count': {'min': 50, 'max': 200},
        'headings': {'min': 2, 'max': 5},
        'images': {'min': 1, 'max': 3}
    }
    terms = [
        {'term': 'кето дієта', 'term_normalized': 'кето дієта', 'min_recommended': 3, 'max_recommended': 5}
    ]
    
    score = compute_content_score(draft, guidelines, terms, 'html')
    
    # Should have low term coverage score
    assert score['total_score'] < 30
    assert score['breakdown']['term_coverage']['score'] == 0


def test_perfect_coverage_score():
    """Test score with perfect term coverage."""
    draft = """
    <h1>Кето дієта</h1>
    <p>Кето дієта - це низьковуглеводна дієта. Кето дієта допомагає схуднути.</p>
    <h2>Переваги кето дієти</h2>
    <p>Низьковуглеводна дієта має багато переваг. Кето дієта ефективна.</p>
    <p>Схуднення на кето дієті. Низьковуглеводна їжа.</p>
    <img src="keto.jpg">
    """
    
    guidelines = {
        'word_count': {'min': 20, 'max': 100},
        'headings': {'min': 2, 'max': 5},
        'images': {'min': 1, 'max': 3}
    }
    
    terms = [
        {'term': 'кето дієта', 'term_normalized': 'кето дієта', 'min_recommended': 3, 'max_recommended': 6},
        {'term': 'низьковуглеводна', 'term_normalized': 'низьковуглеводна', 'min_recommended': 2, 'max_recommended': 4},
        {'term': 'схуднути', 'term_normalized': 'схуднути', 'min_recommended': 1, 'max_recommended': 2}
    ]
    
    score = compute_content_score(draft, guidelines, terms, 'html')
    
    # Should have high score
    assert score['total_score'] > 70
    assert score['breakdown']['term_coverage']['score'] > 40


def test_over_optimization_penalty():
    """Test penalty for keyword stuffing."""
    draft = """
    <h1>Кето кето кето</h1>
    <p>Кето кето кето кето кето кето кето кето кето кето.</p>
    <p>Кето кето кето кето кето кето кето кето кето кето.</p>
    <p>Кето кето кето кето кето кето кето кето кето кето.</p>
    """
    
    guidelines = {
        'word_count': {'min': 10, 'max': 100},
        'headings': {'min': 1, 'max': 5},
        'images': {'min': 0, 'max': 3}
    }
    
    terms = [
        {'term': 'кето', 'term_normalized': 'кето', 'min_recommended': 2, 'max_recommended': 5}
    ]
    
    score = compute_content_score(draft, guidelines, terms, 'html')
    
    # Term coverage should be penalized (кето appears way too many times)
    term_detail = score['term_details'][0]
    assert term_detail['status'] == 'high'
    assert term_detail['current'] > 15


def test_under_optimization():
    """Test score when terms are used below minimum."""
    draft = """
    <h1>Title</h1>
    <p>Some content with кето mentioned once.</p>
    <p>More content here.</p>
    """
    
    guidelines = {
        'word_count': {'min': 10, 'max': 100},
        'headings': {'min': 1, 'max': 5},
        'images': {'min': 0, 'max': 3}
    }
    
    terms = [
        {'term': 'кето', 'term_normalized': 'кето', 'min_recommended': 5, 'max_recommended': 10}
    ]
    
    score = compute_content_score(draft, guidelines, terms, 'html')
    
    term_detail = score['term_details'][0]
    assert term_detail['status'] == 'low'
    assert term_detail['current'] < term_detail['recommended_min']


def test_structural_issues():
    """Test score with structural problems."""
    # Too short content
    draft = "<p>Short</p>"
    
    guidelines = {
        'word_count': {'min': 500, 'max': 1000},
        'headings': {'min': 3, 'max': 8},
        'images': {'min': 2, 'max': 5}
    }
    
    terms = []
    
    score = compute_content_score(draft, guidelines, terms, 'html')
    
    # Structure score should be low
    assert score['breakdown']['structure']['score'] < 10
    assert score['structure_details']['word_count']['current'] < guidelines['word_count']['min']


def test_headings_score():
    """Test headings scoring component."""
    draft = """
    <h1>Кето дієта</h1>
    <h2>Що таке кето</h2>
    <h2>Переваги</h2>
    <h3>Схуднення</h3>
    <p>Content here.</p>
    """
    
    guidelines = {
        'word_count': {'min': 10, 'max': 100},
        'headings': {'min': 2, 'max': 5},
        'images': {'min': 0, 'max': 3}
    }
    
    terms = [
        {'term': 'кето дієта', 'term_normalized': 'кето дієта', 'min_recommended': 1, 'max_recommended': 3},
        {'term': 'схуднення', 'term_normalized': 'схуднення', 'min_recommended': 1, 'max_recommended': 2}
    ]
    
    score = compute_content_score(draft, guidelines, terms, 'html')
    
    # Should have good headings score (H1 present, H2/H3 count good, terms in headings)
    assert score['breakdown']['headings']['score'] > 10
    assert score['headings_details']['h1_present'] is True
    assert score['headings_details']['terms_in_headings'] >= 1
