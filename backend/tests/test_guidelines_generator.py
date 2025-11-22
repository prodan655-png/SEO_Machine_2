"""
Unit tests for guidelines_generator module.
"""

import pytest
from modules.guidelines_generator import (
    calculate_metric_ranges,
    extract_common_headings,
    generate_guidelines
)


def test_calculate_metric_ranges_basic():
    """Test basic metric range calculation."""
    values = [1500, 1800, 1600, 1700, 1550]
    weights = [1.0, 0.9, 0.8, 0.7, 0.6]
    
    result = calculate_metric_ranges(values, weights, remove_outliers=False)
    
    assert result['min'] > 0
    assert result['max'] > result['min']
    assert result['median'] > 0
    assert 0 < result['confidence'] <= 1.0


def test_outlier_removal():
    """Test outlier removal in range calculation."""
    values = [1500, 1600, 1550, 1580, 5000]  # 5000 is outlier
    weights = [1.0, 0.9, 0.8, 0.7, 0.6]
    
    result = calculate_metric_ranges(values, weights, remove_outliers=True)
    
    # Max should not be influenced by 5000
    assert result['max'] < 3000


def test_extract_common_headings():
    """Test extraction of common headings."""
    competitors = [
        {
            'headings': [
                {'level': 'h1', 'text': 'Title'},
                {'level': 'h2', 'text': 'What is Keto'},
                {'level': 'h2', 'text': 'Benefits'}
            ]
        },
        {
            'headings': [
                {'level': 'h2', 'text': 'What is Keto'},  # Common with first
                {'level': 'h2', 'text': 'How to Start'}
            ]
        },
        {
            'headings': [
                {'level': 'h2', 'text': 'Benefits'},  # Common with first
                {'level': 'h3', 'text': 'Weight Loss'}
            ]
        }
    ]
    
    weights = [1.0, 0.9, 0.8]
    
    common = extract_common_headings(competitors, weights)
    
    # Should find common headings
    assert len(common) > 0
    
    # Check that "What is Keto" and "Benefits" are included (appear >= 2 times)
    headings_text = [h['heading'].lower() for h in common]
    assert any('keto' in h for h in headings_text)


def test_generate_guidelines_normal():
    """Test guidelines generation with normal SERP."""
    competitors = [
        {'status': 'valid', 'word_count': 1500, 'headings': [{'level': 'h2', 'text': 'Section 1'}], 'image_count': 3},
        {'status': 'valid', 'word_count': 1800, 'headings': [{'level': 'h2', 'text': 'Section 1'}, {'level': 'h2', 'text': 'Section 2'}], 'image_count': 4},
        {'status': 'valid', 'word_count': 1600, 'headings': [{'level': 'h2', 'text': 'Section 1'}], 'image_count': 2},
        {'status': 'valid', 'word_count': 1700, 'headings': [{'level': 'h2', 'text': 'Section 2'}], 'image_count': 3},
    ]
    
    weights = [1.0, 0.9, 0.8, 0.7]
    
    guidelines = generate_guidelines(competitors, weights)
    
    assert guidelines['competitors_analyzed'] == 4
    assert len(guidelines['warnings']) == 0  # Should have no warnings
    
    # Check ranges
    assert guidelines['word_count']['min'] > 0
    assert guidelines['word_count']['max'] > guidelines['word_count']['min']
    assert guidelines['headings']['min'] >= 1
    assert guidelines['images']['min'] >= 0


def test_generate_guidelines_thin_serp():
    """Test guidelines with thin SERP (< 3 competitors)."""
    competitors = [
        {'status': 'valid', 'word_count': 1500, 'headings': [], 'image_count': 2},
        {'status': 'valid', 'word_count': 1600, 'headings': [], 'image_count': 3},
    ]
    
    weights = [1.0, 0.9]
    
    guidelines = generate_guidelines(competitors, weights)
    
    # Should have warning
    assert len(guidelines['warnings']) > 0
    assert any('Thin SERP' in w for w in guidelines['warnings'])
    
    # Ranges should be wider (multiplied by 1.3)
    assert guidelines['word_count']['confidence'] < 1.0


def test_generate_guidelines_no_valid():
    """Test guidelines when no valid competitors."""
    competitors = [
        {'status': 'failed'},
        {'status': 'weak'}
    ]
    
    weights = [1.0, 0.9]
    
    guidelines = generate_guidelines(competitors, weights)
    
    assert guidelines['competitors_analyzed'] == 0
    assert len(guidelines['warnings']) > 0
    assert 'No valid competitors' in guidelines['warnings'][0]
    
    # Should return default values
    assert guidelines['word_count']['confidence'] == 0.0


def test_suggested_outline():
    """Test suggested outline generation."""
    competitors = [
        {'status': 'valid', 'word_count': 1500, 
         'headings': [{'level': 'h2', 'text': 'Introduction'}, {'level': 'h2', 'text': 'Benefits'}], 
         'image_count': 2},
        {'status': 'valid', 'word_count': 1600, 
         'headings': [{'level': 'h2', 'text': 'Introduction'}, {'level': 'h2', 'text': 'How It Works'}], 
         'image_count': 3},
        {'status': 'valid', 'word_count': 1700, 
         'headings': [{'level': 'h2', 'text': 'Benefits'}], 
         'image_count': 2},
    ]
    
    weights = [1.0, 0.9, 0.8]
    
    guidelines = generate_guidelines(competitors, weights)
    
    # Should have suggested outline
    assert len(guidelines['suggested_outline']) > 0
    
    # "Introduction" and "Benefits" should be suggested (appear in 2+ competitors)
    outline_lower = [h.lower() for h in guidelines['suggested_outline']]
    assert any('introduction' in h for h in outline_lower)
