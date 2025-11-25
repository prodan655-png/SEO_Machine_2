"""
Scoring Constants and Configuration
Defines versioned scoring rules and weights
"""

# Current scoring version
SCORING_VERSION = "1.0.0"

# Scoring weights (must sum to 100)
SCORING_WEIGHTS = {
    "terms": 60,        # Term coverage score (out of 60 points)
    "structure": 20,    # Structure score (out of 20 points)
    "headings": 20      # Headings score (out of 20 points)
}

# Term coverage scoring rules
TERM_COVERAGE_CONFIG = {
    "over_optimization_multiplier": 1.5,  # Count > max * this = penalty
    "under_penalty_linear": True          # Linear decrease when under min
}

# Structure scoring rules
STRUCTURE_CONFIG = {
    "word_count_weight": 10,    # Out of 20 structure points
    "images_weight": 5,
    "paragraphs_weight": 5
}

# Headings scoring rules
HEADINGS_CONFIG = {
    "h1_weight": 5,                     # H1 presence
    "h2_h3_count_weight": 10,          # H2/H3 count in range
    "terms_in_headings_weight": 5      # Important terms in headings
}

# Changelog for version tracking
SCORING_CHANGELOG = {
    "1.0.0": {
        "date": "2025-11-25",
        "changes": [
            "Initial versioned scoring system",
            "Terms: 60pts, Structure: 20pts, Headings: 20pts",
            "Over-optimization penalty at 1.5x max",
            "Linear under-optimization penalty"
        ]
    }
}


def get_scoring_config(version: str = SCORING_VERSION) -> dict:
    """
    Get scoring configuration for a specific version.
    
    Args:
        version: Scoring version (default: current)
        
    Returns:
        Dict with weights and rules for that version
    """
    # For now, only v1.0.0 exists
    if version != "1.0.0":
        raise ValueError(f"Unknown scoring version: {version}")
    
    return {
        "version": version,
        "weights": SCORING_WEIGHTS,
        "term_coverage": TERM_COVERAGE_CONFIG,
        "structure": STRUCTURE_CONFIG,
        "headings": HEADINGS_CONFIG
    }
