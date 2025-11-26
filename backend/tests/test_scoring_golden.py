import pytest
from modules.content_scorer import compute_content_score, calculate_term_coverage_score

# Mock Data
MOCK_GUIDELINES = {
    'word_count': {'min': 100, 'max': 200, 'median': 150},
    'headings': {'min': 2, 'max': 5, 'median': 3},
    'images': {'min': 1, 'max': 3, 'median': 2}
}

MOCK_TERMS = [
    {'term': 'keyword', 'term_normalized': 'keyword', 'min_recommended': 2, 'max_recommended': 5},
    {'term': 'seo', 'term_normalized': 'seo', 'min_recommended': 1, 'max_recommended': 3}
]

def test_scoring_monotonicity_terms():
    """Test that adding relevant terms increases score, and deleting doesn't increase it (unless over-optimized)."""
    
    # Case 1: Under-optimized -> Optimal
    text_low = "This is a text with keyword." # 1 keyword (min 2)
    score_low = calculate_term_coverage_score(text_low, MOCK_TERMS, {})['score']
    
    text_optimal = "This is a text with keyword and another keyword." # 2 keywords (min 2)
    score_optimal = calculate_term_coverage_score(text_optimal, MOCK_TERMS, {})['score']
    
    assert score_optimal > score_low, "Adding terms to reach min should increase score"
    
    # Case 2: Optimal -> Optimal (more terms but within max)
    text_more = text_optimal + " And another keyword." # 3 keywords (max 5)
    score_more = calculate_term_coverage_score(text_more, MOCK_TERMS, {})['score']
    
    assert score_more >= score_optimal, "Adding terms within max should not decrease score"

def test_scoring_over_optimization_decay():
    """Test smooth decay for over-optimization."""
    
    # Max is 5. 
    # 6 keywords -> Slightly over (linear decay)
    # 10 keywords -> Heavily over (hyperbolic decay)
    
    base_text = "keyword " * 5 # Optimal (score 1.0)
    score_optimal = calculate_term_coverage_score(base_text, MOCK_TERMS, {})['term_details'][0]['term_score']
    assert score_optimal == 1.0
    
    # Slightly over
    text_slightly_over = "keyword " * 6 # 6 > 5
    score_slightly_over = calculate_term_coverage_score(text_slightly_over, MOCK_TERMS, {})['term_details'][0]['term_score']
    
    assert score_slightly_over < 1.0, "Score should decrease when over-optimized"
    assert score_slightly_over > 0.5, "Score should not drop too sharply for slight over-optimization"
    
    # Heavily over
    text_heavily_over = "keyword " * 20 # Way over
    score_heavily_over = calculate_term_coverage_score(text_heavily_over, MOCK_TERMS, {})['term_details'][0]['term_score']
    
    assert score_heavily_over < score_slightly_over, "More over-optimization should yield lower score"
    assert score_heavily_over > 0.0, "Score should never be exactly 0 for relevant content"

def test_structure_monotonicity():
    """Test that adding words (up to a point) increases score."""
    # TODO: Implement full structure test if needed
    pass

def test_golden_scenarios():
    """Golden tests for overall score ranges."""
    
    # 1. Empty Draft
    score_empty = compute_content_score("", MOCK_GUIDELINES, MOCK_TERMS)
    assert score_empty['total_score'] == 0
    
    # 2. Perfect Draft
    text_perfect = """
    <h1>Title with keyword</h1>
    <h2>Subtitle with seo</h2>
    <p>keyword keyword keyword. seo. word word word...</p>
    """ + " word" * 100 # Add words to meet count
    
    score_perfect = compute_content_score(text_perfect, MOCK_GUIDELINES, MOCK_TERMS)
    assert score_perfect['total_score'] > 80, "Perfect draft should have high score"

if __name__ == "__main__":
    # Manual run
    try:
        test_scoring_monotonicity_terms()
        test_scoring_over_optimization_decay()
        test_golden_scenarios()
        print("✅ All tests passed!")
    except AssertionError as e:
        print(f"❌ Test failed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
