"""
Mock implementation of AI modules for development.
Returns template responses without consuming AI tokens.
"""

from typing import Dict, Any, List
from logger import setup_logger

logger = setup_logger(__name__)


def mock_generate_brief(
    analysis_id: str,
    content_type: str = "blog",
    tone: str = "neutral"
) -> Dict[str, Any]:
    """
    Mock AI brief generator.
    
    Returns template brief structure without calling LLM.
    """
    logger.info(f"[MOCK] Generating brief for analysis {analysis_id}")
    
    return {
        "h1": f"Complete Guide to Your Topic - {content_type.title()} Edition",
        "sections": [
            {
                "h2": "Introduction to the Topic",
                "h3": ["What You Need to Know", "Why This Matters"],
                "talking_points": [
                    "Start with a compelling hook",
                    "Explain the main concept clearly",
                    "Preview what readers will learn"
                ]
            },
            {
                "h2": "Key Concepts and Definitions",
                "h3": ["Basic Terminology", "Common Misconceptions"],
                "talking_points": [
                    "Define important terms",
                    "Clear up common misunderstandings",
                    "Provide examples"
                ]
            },
            {
                "h2": "Practical Applications",
                "h3": ["Step-by-Step Guide", "Best Practices"],
                "talking_points": [
                    "Give actionable advice",
                    "Include real-world examples",
                    "Share expert tips"
                ]
            }
        ],
        "faqs": [
            "What is the main benefit?",
            "How long does it take?",
            "What are common challenges?",
            "Is it suitable for beginners?"
        ],
        "meta": {
            "estimated_word_count": 1500,
            "sections_count": 3,
            "tokens_used": 0
        }
    }


def mock_enhance_content(
    fragment: str,
    target_terms: List[str],
    max_words: int = 200,
    style: str = "neutral"
) -> Dict[str, Any]:
    """
    Mock content enhancer.
    
    Returns original text with annotation instead of actual enhancement.
    """
    logger.info(f"[MOCK] Enhancing content fragment ({len(fragment)} chars)")
    
    enhanced = f"{fragment}\n\n[MOCK: In production, this would be enhanced with terms: {', '.join(target_terms[:3])}...]"
    
    return {
        "original_length": len(fragment.split()),
        "enhanced_text": enhanced,
        "new_length": len(enhanced.split()),
        "terms_added": [
            {"term": term, "count": 1, "positions": [len(fragment)]}
            for term in target_terms[:2]
        ],
        "tokens_used": 0
    }


def mock_generate_meta(analysis_id: str) -> Dict[str, Any]:
    """
    Mock meta tags generator.
    
    Returns template title, description, and H1 variants.
    """
    logger.info(f"[MOCK] Generating meta tags for analysis {analysis_id}")
    
    return {
        "titles": [
            {"text": "Your Topic: Complete Guide 2025 | Expert Tips & Advice", "length": 50, "keyword_included": True},
            {"text": "Everything You Need to Know About Your Topic", "length": 46, "keyword_included": True},
            {"text": "Master Your Topic: Beginner to Expert Guide", "length": 44, "keyword_included": True}
        ],
        "descriptions": [
            {"text": "Discover everything about your topic ✓ Expert tips ✓ Practical guide ✓ Latest 2025 updates ✓ Start today!", "length": 107},
            {"text": "Learn your topic with our comprehensive guide. Includes tips, examples, and expert advice for all levels.", "length": 105}
        ],
        "h1_variants": [
            "The Complete Guide to Your Topic",
            "Everything You Need to Know About Your Topic",
            "Your Topic: Expert Guide for 2025"
        ],
        "intro_paragraphs": [
            "Looking to learn about your topic? This comprehensive guide covers everything from basics to advanced techniques, helping you achieve your goals efficiently."
        ],
        "tokens_used": 0
    }


def mock_generate_coach(
    current_score: int,
    target_score: int,
    breakdown: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Mock score coach / explainer.
    
    Returns template improvement steps.
    """
    logger.info(f"[MOCK] Generating improvement plan (current: {current_score}, target: {target_score})")
    
    gap = target_score - current_score
    
    return {
        "current_score": current_score,
        "target_score": target_score,
        "gap": gap,
        "improvement_steps": [
            {
                "priority": "high",
                "action": "Add 3-5 more instances of your top terms throughout the content",
                "expected_gain": min(8, gap // 2),
                "category": "terms",
                "difficulty": "easy"
            },
            {
                "priority": "high",
                "action": "Expand the content by 200-300 words to meet recommended length",
                "expected_gain": min(5, gap // 3),
                "category": "structure",
                "difficulty": "medium"
            },
            {
                "priority": "medium",
                "action": "Add 1-2 more images or infographics",
                "expected_gain": min(3, gap // 4),
                "category": "structure",
                "difficulty": "easy"
            },
            {
                "priority": "medium",
                "action": "Include key terms in at least 2 subheadings (H2/H3)",
                "expected_gain": min(4, gap // 4),
                "category": "headings",
                "difficulty": "easy"
            }
        ],
        "summary": f"Focus on terms (+{min(8, gap // 2)}) and structure (+{min(5, gap // 3)}) for biggest gains",
        "tokens_used": 0
    }


def mock_analyze_intent(analysis_id: str) -> Dict[str, Any]:
    """
    Mock competitor intent analyzer.
    
    Returns template intent classification.
    """
    logger.info(f"[MOCK] Analyzing search intent for analysis {analysis_id}")
    
    return {
        "intent": {
            "primary": "informational",
            "secondary": "commercial",
            "confidence": 0.75
        },
        "competitor_summaries": [
            {
                "position": 1,
                "url": "example.com/article",
                "summary": "[MOCK] Comprehensive guide covering basics and advanced topics with practical examples."
            },
            {
                "position": 2,
                "url": "example2.com/guide",
                "summary": "[MOCK] Step-by-step tutorial focused on beginners with visual aids."
            }
        ],
        "common_topics": [
            {"topic": "Basic introduction and overview", "coverage": "9/10"},
            {"topic": "Practical how-to guide", "coverage": "8/10"},
            {"topic": "Common mistakes to avoid", "coverage": "7/10"}
        ],
        "content_gaps": [
            "[MOCK] Advanced techniques section",
            "[MOCK] Comparison with alternatives",
            "[MOCK] Real user case studies"
        ],
        "recommendations": [
            "[MOCK] Add a comparison table",
            "[MOCK] Include expert quotes or testimonials",
            "[MOCK] Create a downloadable checklist"
        ],
        "tokens_used": 0
    }
