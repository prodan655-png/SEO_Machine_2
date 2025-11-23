"""
Content Iterator Module.
Manages iterative content improvements with score validation.
"""

from typing import Dict, List, Any, Optional
from modules.ai.ai_client import get_ai_client
from modules.content_scorer import compute_content_score
from logger import setup_logger

logger = setup_logger(__name__)


class ContentIterator:
    """Manages iterative content improvements with score tracking."""
    
    def __init__(self):
        """Initialize Content Iterator."""
        self.ai_client = get_ai_client()
        self.history = []
    
    async def improve_step_by_step(
        self,
        content: str,
        guidelines: Dict[str, Any],
        terms: List[Dict[str, Any]],
        current_score: int,
        target_score: int,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Improve content iteratively, one change at a time.
        
        Args:
            content: Current content HTML
            guidelines: Content guidelines
            terms: List of terms with recommendations
            current_score: Current total score
            target_score: Desired target score
            max_iterations: Maximum number of iterations
            
        Returns:
            Dict with final content, score, and iteration history
        """
        logger.info(f"Starting iterative improvement: {current_score} → {target_score}")
        
        iterations = []
        current_content = content
        current_total_score = current_score
        
        for step in range(1, max_iterations + 1):
            logger.info(f"Iteration {step}/{max_iterations}")
            
            # Check if target reached
            if current_total_score >= target_score:
                logger.info(f"Target score {target_score} reached!")
                break
            
            # Get next action
            action = await self._get_next_action(
                current_content,
                guidelines,
                terms,
                current_total_score,
                target_score
            )
            
            if not action:
                logger.warning("No more actions available")
                break
            
            # Apply action
            new_content = await self._apply_action(
                current_content,
                action,
                guidelines,
                terms
            )
            
            # Calculate new score
            score_result = compute_content_score(
                new_content,
                guidelines,
                terms,
                format='html'
            )
            new_score = score_result['total_score']
            
            # Validate improvement
            from modules.ai.score_validator import ScoreValidator
            validator = ScoreValidator()
            validation = validator.validate_improvement(
                current_content,
                new_content,
                current_total_score,
                new_score
            )
            
            iteration_result = {
                'step': step,
                'action': action['description'],
                'old_score': current_total_score,
                'new_score': new_score,
                'score_delta': new_score - current_total_score,
                'content': new_content,
                'success': validation['valid'],
                'reason': validation.get('reason', '')
            }
            
            if validation['valid']:
                # Accept change
                current_content = new_content
                current_total_score = new_score
                logger.info(f"✅ Step {step}: {current_total_score} (+{validation['score_delta']})")
            else:
                # Reject change (rollback)
                logger.warning(f"❌ Step {step} rejected: {validation['reason']}")
                iteration_result['rolled_back'] = True
            
            iterations.append(iteration_result)
        
        return {
            'final_content': current_content,
            'final_score': current_total_score,
            'initial_score': current_score,
            'target_score': target_score,
            'iterations': iterations,
            'success': current_total_score >= target_score,
            'improvements_made': len([i for i in iterations if i['success']])
        }
    
    async def _get_next_action(
        self,
        content: str,
        guidelines: Dict[str, Any],
        terms: List[Dict[str, Any]],
        current_score: int,
        target_score: int
    ) -> Optional[Dict[str, Any]]:
        """
        Determine the next single action to take.
        
        Returns:
            Dict with action details or None if no action needed
        """
        # Re-score to get current breakdown
        score_result = compute_content_score(content, guidelines, terms, 'html')
        breakdown = score_result['breakdown']
        term_details = score_result['term_details']
        
        # Prioritize actions
        actions = []
        
        # 1. Check for missing/low terms (highest priority)
        for term in term_details:
            if term['status'] == 'low':
                needed = term['recommended_min'] - term['current']
                actions.append({
                    'type': 'add_term',
                    'priority': 1,
                    'impact': needed * 2,  # Estimate score impact
                    'description': f"Додати термін '{term['term']}' {needed} раз(и) (зараз: {term['current']}, норма: {term['recommended_min']}-{term['recommended_max']})",
                    'term': term['term'],
                    'count': needed
                })
        
        # 2. Check for over-optimized terms
        for term in term_details:
            if term['status'] == 'high':
                excess = term['current'] - term['recommended_max']
                actions.append({
                    'type': 'reduce_term',
                    'priority': 2,
                    'impact': excess * 1.5,
                    'description': f"Зменшити термін '{term['term']}' на {excess} раз(и) (зараз: {term['current']}, норма: {term['recommended_min']}-{term['recommended_max']})",
                    'term': term['term'],
                    'count': excess
                })
        
        # 3. Check headings
        headings_details = score_result['headings_details']
        h2_h3_current = headings_details['h2_h3_count']['current']
        h_min = guidelines['headings']['min']
        
        if h2_h3_current < h_min:
            needed = h_min - h2_h3_current
            actions.append({
                'type': 'add_headings',
                'priority': 3,
                'impact': needed * 3,
                'description': f"Додати {needed} заголовк(ів) H2/H3 (зараз: {h2_h3_current}, норма: {h_min}+)",
                'count': needed
            })
        
        # 4. Check word count
        structure_details = score_result['structure_details']
        wc_current = structure_details['word_count']['current']
        wc_min = guidelines['word_count']['min']
        
        if wc_current < wc_min:
            needed = wc_min - wc_current
            actions.append({
                'type': 'expand_content',
                'priority': 4,
                'impact': (needed / 100) * 2,
                'description': f"Розширити контент на {needed} слів (зараз: {wc_current}, норма: {wc_min}+)",
                'count': needed
            })
        
        # Sort by priority and impact
        actions.sort(key=lambda x: (x['priority'], -x['impact']))
        
        return actions[0] if actions else None
    
    async def _apply_action(
        self,
        content: str,
        action: Dict[str, Any],
        guidelines: Dict[str, Any],
        terms: List[Dict[str, Any]]
    ) -> str:
        """
        Apply a single action to the content.
        
        Args:
            content: Current content
            action: Action to apply
            guidelines: Content guidelines
            terms: Terms list
            
        Returns:
            Modified content
        """
        action_type = action['type']
        
        prompt = f"""Ти редактор контенту. Твоє завдання - зробити ОДНУ конкретну зміну в тексті.

ПОТОЧНИЙ КОНТЕНТ:
{content}

ЗАВДАННЯ:
{action['description']}

ПРАВИЛА:
1. Зроби ТІЛЬКИ цю одну зміну
2. НЕ видаляй існуючий контент
3. НЕ змінюй структуру без необхідності
4. Зберігай стиль і тон
5. Інтегруй зміни природньо

Поверни ПОВНИЙ оновлений HTML контент:
"""
        
        try:
            new_content = await self.ai_client.generate_content(
                prompt,
                temperature=0.5,
                max_tokens=8000
            )
            
            # Clean up markdown artifacts
            import re
            new_content = re.sub(r'^```html\s*', '', new_content, flags=re.MULTILINE)
            new_content = re.sub(r'\s*```$', '', new_content, flags=re.MULTILINE)
            new_content = new_content.strip()
            
            return new_content
            
        except Exception as e:
            logger.error(f"Failed to apply action: {e}")
            return content  # Return original on error


# Convenience function
async def improve_iteratively(
    content: str,
    guidelines: Dict[str, Any],
    terms: List[Dict[str, Any]],
    current_score: int,
    target_score: int,
    max_iterations: int = 5
) -> Dict[str, Any]:
    """Convenience wrapper for ContentIterator."""
    iterator = ContentIterator()
    return await iterator.improve_step_by_step(
        content,
        guidelines,
        terms,
        current_score,
        target_score,
        max_iterations
    )
