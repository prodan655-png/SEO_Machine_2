"""
Unit tests for semantic_analyzer module.
"""

import pytest
from modules.semantic_analyzer import (
    compute_tfidf_terms,
    merge_and_rank_terms,
    calculate_term_ranges
)


def test_compute_tfidf_basic():
    """Test TF-IDF computation with simple corpus."""
    docs = [
        "кето дієта для схуднення",
        "схуднення на кето дієті",
        "кето дієта правила та поради"
    ]
    
    terms = compute_tfidf_terms(docs, 'uk', {})
    
    # Should extract terms
    assert len(terms) > 0
    
    # Check that "кето дієта" is among top terms
    term_texts = [t[0] for t in terms]
    assert any('кето' in t for t in term_texts)


def test_tfidf_with_stop_words():
    """Test that stop words are filtered."""
    docs = [
        "це є в на та і",  # All stop words
        "кето дієта"  # Real terms
    ]
    
    terms = compute_tfidf_terms(docs, 'uk', {})
    
    # Stop words should be filtered
    term_texts = [t[0].lower() for t in terms]
    assert 'це' not in term_texts
    assert 'є' not in term_texts


def test_merge_and_rank():
    """Test merging TF-IDF and entity terms."""
    tfidf_terms = [
        ('кето дієта', 0.8),
        ('схуднення', 0.6)
    ]
    
    entities = [
        ('кето дієта', 0.5),  # Overlaps with TF-IDF
        ('dr. berg', 0.4)  # New entity
    ]
    
    merged = merge_and_rank_terms(tfidf_terms, entities, {})
    
    assert len(merged) >= 2
    
    # "кето дієта" should have boosted score
    keto_term = next((t for t in merged if t['term'] == 'кето дієта'), None)
    assert keto_term is not None
    assert keto_term['type'] == 'entity'  # Should be marked as entity
    assert keto_term['score'] > 0.8  # Boosted


def test_calculate_term_ranges():
    """Test term range calculation with SERP weights."""
    terms = [
        {'term': 'кето', 'term_normalized': 'кето', 'type': 'phrase', 'score': 0.8}
    ]
    
    competitor_texts = [
        "кето кето кето",  # 3 occurrences (position 1, weight 1.0)
        "кето кето кето кето",  # 4 occurrences (position 2, weight 0.9)
        "кето кето",  # 2 occurrences (position 3, weight 0.8)
        "кето кето кето",  # 3 occurrences (position 4, weight 0.7)
    ]
    
    serp_weights = [1.0, 0.9, 0.8, 0.7]
    
    results = calculate_term_ranges(terms, competitor_texts, serp_weights)
    
    assert len(results) == 1
    
    term = results[0]
    assert term['term'] == 'кето'
    assert term['min_recommended'] >= 1
    assert term['max_recommended'] > term['min_recommended']
    assert term['docs_used_in'] == 4


def test_term_filtering_by_min_docs():
    """Test that terms appearing in < 3 docs are filtered."""
    terms = [
        {'term': 'rare', 'term_normalized': 'rare', 'type': 'phrase', 'score': 0.5}
    ]
    
    competitor_texts = [
        "rare content",  # Only in 1 document
        "other content",
        "more content",
        "additional content"
    ]
    
    serp_weights = [1.0, 0.9, 0.8, 0.7]
    
    results = calculate_term_ranges(terms, competitor_texts, serp_weights)
    
    # "rare" should be filtered out (appears in only 1 doc)
    assert len(results) == 0


def test_outlier_removal():
    """Test outlier removal in range calculation."""
    terms = [
        {'term': 'test', 'term_normalized': 'test', 'type': 'phrase', 'score': 0.8}
    ]
    
    competitor_texts = [
        " ".join(["test"] * 5),  # 5 occurrences
        " ".join(["test"] * 6),  # 6 occurrences
        " ".join(["test"] * 5),  # 5 occurrences
        " ".join(["test"] * 50),  # 50 occurrences (outlier!)
    ]
    
    serp_weights = [1.0, 0.9, 0.8, 0.7]
    
    results = calculate_term_ranges(terms, competitor_texts, serp_weights)
    
    assert len(results) == 1
    
    # Max should not be influenced too much by the outlier (50)
    term = results[0]
    assert term['max_recommended'] < 20  # Should filter out the 50
