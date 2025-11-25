"""
Score Validator Module
Validates AI-generated content changes by comparing scores before/after
Ensures AI suggestions improve (or at least don't harm) content quality
"""

from typing import Dict, List, Any
try:
    from modules.content_scorer import compute_content_score
    from logger import setup_logger
except ImportError:
    from content_scorer import compute_content_scorer
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from logger import setup_logger

logger = setup_logger(__name__)


def validate_ai_changes(
    original_content: str,
    modified_content: str,
    guidelines: Dict[str, Any],
    terms: List[Dict[str, Any]],
    content_format: str = "html"
) -> Dict[str, Any]:
    """
    Validate AI content changes by comparing scores.
    
    Args:
        original_content: Original HTML/Markdown content
        modified_content: AI-modified HTML/Markdown content
        guidelines: Scoring guidelines (word count, headings, images)
        terms: List of important terms with recommendations
        content_format: 'html' or 'markdown'
        
    Returns:
        {
            "is_valid": bool,           # True if improvement or neutral
            "score_before": int,        # Original score (0-100)
            "score_after": int,         # Modified score (0-100)
            "score_delta": int,         # Difference (positive = improvement)
            "scoring_version": str,     # Version used
            "warnings": List[str],      # List of warnings
            "details": {
                "term_coverage_delta": int,
                "structure_delta": int,
                "headings_delta": int
            }
        }
    """
    logger.info("Validating AI content changes...")
    
    # Score original content
    try:
        score_before_result = compute_content_score(
            original_content,
            guidelines,
            terms,
            content_format
        )
        score_before = score_before_result['total_score']
    except Exception as e:
        logger.error(f"Failed to score original content: {e}")
        return {
            "is_valid": False,
            "error": f"Failed to score original: {str(e)}",
            "warnings": ["Could not validate - scoring failed"]
        }
    
    # Score modified content
    try:
        score_after_result = compute_content_score(
            modified_content,
            guidelines,
            terms,
            content_format
        )
        score_after = score_after_result['total_score']
    except Exception as e:
        logger.error(f"Failed to score modified content: {e}")
        return {
            "is_valid": False,
            "error": f"Failed to score modified: {str(e)}",
            "warnings": ["Could not validate - scoring failed"]
        }
    
    # Calculate delta
    score_delta = score_after - score_before
    
    # Calculate breakdown deltas
    term_delta = (score_after_result['breakdown']['term_coverage']['score'] - 
                  score_before_result['breakdown']['term_coverage']['score'])
    structure_delta = (score_after_result['breakdown']['structure']['score'] - 
                       score_before_result['breakdown']['structure']['score'])
    headings_delta = (score_after_result['breakdown']['headings']['score'] - 
                      score_before_result['breakdown']['headings']['score'])
    
    # Generate warnings
    warnings = []
    is_valid = True
    
    if score_delta < 0:
        warnings.append(f"⚠️ Score DECREASED by {abs(score_delta)} points")
        is_valid = False
        logger.warning(f"AI changes decreased score: {score_before} → {score_after}")
    elif score_delta == 0:
        warnings.append("ℹ️ Score unchanged - no improvement detected")
        logger.info("AI changes did not improve score")
    else:
        logger.info(f"✅ AI changes improved score by {score_delta} points")
    
    # Component-specific warnings
    if term_delta < -5:
        warnings.append(f"Term coverage decreased significantly ({term_delta}pts)")
    if structure_delta < -3:
        warnings.append(f"Structure quality decreased ({structure_delta}pts)")
    if headings_delta < -3:
        warnings.append(f"Heading quality decreased ({headings_delta}pts)")
    
    result = {
        "is_valid": is_valid,
        "score_before": score_before,
        "score_after": score_after,
        "score_delta": score_delta,
        "scoring_version": score_after_result.get('scoring_version', 'unknown'),
        "warnings": warnings,
        "details": {
            "term_coverage_delta": term_delta,
            "structure_delta": structure_delta,
            "headings_delta": headings_delta
        }
    }
    
    logger.info(f"Validation result: {score_before} → {score_after} (Δ{score_delta:+d}), valid={is_valid}")
    
    return result


def validate_ai_suggestion(
    original_content: str,
    ai_suggestion: str,
    analysis_id: str,
    db_session
) -> Dict[str, Any]:
    """
    Validate AI suggestion using analysis guidelines from database.
    
    Args:
        original_content: Current content
        ai_suggestion: Proposed AI changes
        analysis_id: Analysis ID to fetch guidelines/terms
        db_session: Database session
        
    Returns:
        Validation result dict (same as validate_ai_changes)
    """
    from database import Analysis, Term, Guideline
    
    # Fetch analysis data
    analysis = db_session.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        return {
            "is_valid": False,
            "error": f"Analysis {analysis_id} not found",
            "warnings": ["Cannot validate without analysis data"]
        }
    
    # Fetch terms and guidelines
    terms = db_session.query(Term).filter(Term.analysis_id == analysis_id).all()
    guideline = db_session.query(Guideline).filter(Guideline.analysis_id == analysis_id).first()
    
    if not terms or not guideline:
        return {
            "is_valid": False,
            "error": "Missing terms or guidelines",
            "warnings": ["Cannot validate without complete analysis data"]
        }
    
    # Format data
    terms_data = [
        {
            'term': t.term,
            'term_normalized': t.term_normalized,
            'min_recommended': t.min_recommended,
            'max_recommended': t.max_recommended
        }
        for t in terms
    ]
    
    guidelines_data = {
        'word_count': {
            'min': guideline.word_count_min,
            'max': guideline.word_count_max,
            'median': guideline.word_count_median
        },
        'headings': {
            'min': guideline.headings_min,
            'max': guideline.headings_max,
            'median': guideline.headings_median
        },
        'images': {
            'min': guideline.images_min,
            'max': guideline.images_max,
            'median': guideline.images_median
        }
    }
    
    # Validate
    return validate_ai_changes(
        original_content,
        ai_suggestion,
        guidelines_data,
        terms_data,
        content_format="html"
    )


if __name__ == "__main__":
    # Add parent to path for standalone execution
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    
    # Simple test
    test_guidelines = {
        'word_count': {'min': 100, 'max': 200, 'median': 150},
        'headings': {'min': 2, 'max': 5, 'median': 3},
        'images': {'min': 1, 'max': 3, 'median': 2}
    }
    
    test_terms = [
        {'term': 'SEO', 'term_normalized': 'seo', 'min_recommended': 3, 'max_recommended': 8},
        {'term': 'content', 'term_normalized': 'content', 'min_recommended': 5, 'max_recommended': 12}
    ]
    
    original = """
    <h1>SEO Guide</h1>
    <p>Content about SEO and content optimization.</p>
    <h2>Tips</h2>
    <p>Some SEO content tips here.</p>
    <img src="test.jpg">
    """
    
    # Good changes (adds more relevant content)
    improved = """
    <h1>SEO Guide</h1>
    <p>Content about SEO and content optimization. SEO content strategies.</p>
    <h2>SEO Tips</h2>
    <p>Some SEO content tips here. More content about SEO techniques.</p>
    <h2>Content Strategy</h2>
    <p>SEO content planning and execution.</p>
    <img src="test.jpg">
    <img src="test2.jpg">
    """
    
    # Bad changes (removes content)
    degraded = """
    <h1>Guide</h1>
    <p>Some tips.</p>
    """
    
    print("Testing Score Validator")
    print("=" * 60)
    
    print("\n[TEST 1] Good Changes (should be valid)")
    result1 = validate_ai_changes(original, improved, test_guidelines, test_terms)
    print(f"Valid: {result1['is_valid']}")
    print(f"Score: {result1['score_before']} → {result1['score_after']} (Δ{result1['score_delta']:+d})")
    print(f"Warnings: {result1['warnings']}")
    
    print("\n[TEST 2] Bad Changes (should be invalid)")
    result2 = validate_ai_changes(original, degraded, test_guidelines, test_terms)
    print(f"Valid: {result2['is_valid']}")
    print(f"Score: {result2['score_before']} → {result2['score_after']} (Δ{result2['score_delta']:+d})")
    print(f"Warnings: {result2['warnings']}")
