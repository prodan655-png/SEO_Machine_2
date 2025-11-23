"""
Score Validator Module.
Validates that content changes improve the score.
"""

from typing import Dict, Any
from modules.content_scorer import compute_content_score
from logger import setup_logger

logger = setup_logger(__name__)


class ScoreValidator:
    """Validates score improvements and suggests rollbacks."""
    
    def __init__(self, min_improvement: int = 1):
        """
        Initialize Score Validator.
        
        Args:
            min_improvement: Minimum score improvement to consider valid
        """
        self.min_improvement = min_improvement
    
    def validate_improvement(
        self,
        old_content: str,
        new_content: str,
        old_score: int,
        new_score: int
    ) -> Dict[str, Any]:
        """
        Validate that the new content improves the score.
        
        Args:
            old_content: Original content
            new_content: Modified content
            old_score: Original score
            new_score: New score
            
        Returns:
            Dict with validation result
        """
        score_delta = new_score - old_score
        
        if score_delta >= self.min_improvement:
            return {
                'valid': True,
                'score_delta': score_delta,
                'reason': f'Score improved by {score_delta} points'
            }
        elif score_delta == 0:
            return {
                'valid': False,
                'score_delta': 0,
                'reason': 'No score improvement'
            }
        else:
            return {
                'valid': False,
                'score_delta': score_delta,
                'reason': f'Score decreased by {abs(score_delta)} points'
            }
    
    def analyze_score_change(
        self,
        old_breakdown: Dict[str, Any],
        new_breakdown: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze detailed score changes across categories.
        
        Args:
            old_breakdown: Original score breakdown
            new_breakdown: New score breakdown
            
        Returns:
            Detailed analysis of changes
        """
        changes = {}
        
        for category in ['term_coverage', 'structure', 'headings']:
            old_score = old_breakdown.get(category, {}).get('score', 0)
            new_score = new_breakdown.get(category, {}).get('score', 0)
            delta = new_score - old_score
            
            changes[category] = {
                'old': old_score,
                'new': new_score,
                'delta': delta,
                'improved': delta > 0
            }
        
        return {
            'changes': changes,
            'total_categories_improved': sum(1 for c in changes.values() if c['improved']),
            'total_categories_worsened': sum(1 for c in changes.values() if c['delta'] < 0)
        }
    
    def suggest_rollback(
        self,
        score_delta: int,
        analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Suggest whether to rollback based on score change.
        
        Args:
            score_delta: Total score change
            analysis: Detailed score analysis
            
        Returns:
            Rollback recommendation
        """
        if score_delta < 0:
            return {
                'should_rollback': True,
                'reason': f'Score decreased by {abs(score_delta)} points',
                'confidence': 'high'
            }
        
        if score_delta == 0:
            worsened = analysis.get('total_categories_worsened', 0)
            if worsened > 0:
                return {
                    'should_rollback': True,
                    'reason': f'{worsened} categories worsened despite no total change',
                    'confidence': 'medium'
                }
        
        return {
            'should_rollback': False,
            'reason': 'Score improved or maintained',
            'confidence': 'high'
        }


# Convenience function
def validate_content_change(
    old_content: str,
    new_content: str,
    old_score: int,
    new_score: int,
    min_improvement: int = 1
) -> Dict[str, Any]:
    """Convenience wrapper for ScoreValidator."""
    validator = ScoreValidator(min_improvement=min_improvement)
    return validator.validate_improvement(
        old_content,
        new_content,
        old_score,
        new_score
    )
