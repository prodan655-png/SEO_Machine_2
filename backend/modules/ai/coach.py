"""
SEO Coach Module.
Provides AI-powered personalized SEO coaching based on content score.
"""

from typing import Dict, Any, List, Optional
from modules.ai.ai_client import get_ai_client
from logger import setup_logger

logger = setup_logger(__name__)


class SEOCoach:
    """AI-powered SEO coaching assistant."""
    
    def __init__(self):
        """Initialize SEO Coach."""
        self.ai_client = get_ai_client()
    
    async def generate_coaching(
        self,
        current_score: int,
        target_score: int,
        breakdown: Dict[str, Any],
        term_details: List[Dict[str, Any]],
        structure_details: Optional[Dict[str, Any]] = None,
        headings_details: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate personalized SEO coaching.
        
        Args:
            current_score: Current total score (0-100)
            target_score: Desired score (0-100)
            breakdown: Score breakdown by category
            term_details: List of terms with status
            structure_details: Word count, paragraphs info
            headings_details: Headings analysis
            
        Returns:
            Coaching recommendations dict
        """
        try:
            # Build prompt
            prompt = self._build_prompt(
                current_score,
                target_score,
                breakdown,
                term_details,
                structure_details,
                headings_details
            )
            
            # Get AI response
            response = await self.ai_client.generate_json(prompt, temperature=0.7)
            
            logger.info(f"Generated coaching for score {current_score} → {target_score}")
            return response
            
        except Exception as e:
            logger.error(f"Coaching generation failed: {str(e)}")
            # Return fallback coaching
            return self._get_fallback_coaching(current_score, target_score)
    
    def _build_prompt(
        self,
        current_score: int,
        target_score: int,
        breakdown: Dict[str, Any],
        term_details: List[Dict[str, Any]],
        structure_details: Optional[Dict[str, Any]],
        headings_details: Optional[Dict[str, Any]]
    ) -> str:
        """Build coaching prompt."""
        
        # Extract scores
        terms_score = breakdown.get('terms', {}).get('score', 0)
        terms_max = breakdown.get('terms', {}).get('max', 60)
        structure_score = breakdown.get('structure', {}).get('score', 0)
        structure_max = breakdown.get('structure', {}).get('max', 20)
        headings_score = breakdown.get('headings', {}).get('score', 0)
        headings_max = breakdown.get('headings', {}).get('max', 20)
        
        # Identify problem terms
        term_issues = []
        for term in term_details:
            if term.get('status') == 'low':
                term_issues.append(
                    f"- '{term['term']}': {term['current']} разів (потрібно {term['recommended_min']}-{term['recommended_max']})"
                )
            elif term.get('status') == 'high':
                term_issues.append(
                    f"- '{term['term']}': {term['current']} разів (переспам! норма {term['recommended_min']}-{term['recommended_max']})"
                )
        
        term_issues_text = "\n".join(term_issues[:10]) if term_issues else "Терміни використані правильно"
        
        # Structure issues
        structure_issues = []
        if structure_details:
            wc = structure_details.get('word_count', {})
            if wc.get('current', 0) < wc.get('recommended_min', 0):
                structure_issues.append(
                    f"- Мало слів: {wc['current']} (рекомендовано {wc['recommended_min']}-{wc['recommended_max']})"
                )
        
        structure_issues_text = "\n".join(structure_issues) if structure_issues else "Структура в нормі"
        
        # Headings issues
        headings_issues = []
        if headings_details:
            if not headings_details.get('has_h1'):
                headings_issues.append("- Відсутній H1 заголовок")
            h2_count = headings_details.get('h2_count', 0)
            h2_recommended = headings_details.get('recommended_h2', 4)
            if h2_count < h2_recommended:
                headings_issues.append(
                    f"- Мало H2: {h2_count} (рекомендовано {h2_recommended})"
                )
        
        headings_issues_text = "\n".join(headings_issues) if headings_issues else "Заголовки в нормі"
        
        # Build final prompt
        prompt = f"""Ти досвідчений SEO-спеціаліст. Користувач написав контент і отримав оцінку {current_score}/100.
Мета: досягти {target_score}/100.

ПОТОЧНИЙ СТАН:
- Терміни: {terms_score}/{terms_max} балів
- Структура: {structure_score}/{structure_max} балів
- Заголовки: {headings_score}/{headings_max} балів

ПРОБЛЕМНІ ТЕРМІНИ:
{term_issues_text}

СТРУКТУРНІ ПРОБЛЕМИ:
{structure_issues_text}

ПРОБЛЕМИ З ЗАГОЛОВКАМИ:
{headings_issues_text}

ЗАВДАННЯ:
Створи конкретний план дій для покращення оцінки з {current_score} до {target_score} балів.

ФОРМАТ ВІДПОВІДІ (тільки JSON, без markdown):
{{
    "priority_actions": [
        {{
            "action": "Конкретна дія українською мовою",
            "impact": "high",
            "difficulty": "easy",
            "score_gain": "+X балів",
            "details": "Чому це важливо і як саме зробити"
        }}
    ],
    "content_suggestions": [
        "Конкретна порада про зміст"
    ],
    "term_recommendations": {{
        "add_more": ["термін1", "термін2"],
        "reduce": ["термін3"]
    }},
    "estimated_time": "X-Y хвилин"
}}

ПРАВИЛА:
- Всі тексти тільки УКРАЇНСЬКОЮ мовою
- Тільки дійсні, конкретні, виконувані поради
- Починай з найлегших дій з найбільшим impact
- Не більше 5 priority actions
- Сортуй actions за impact (high → medium → low)
- Реалістично оцінюй score_gain та час
- У details пиши КЯК САМЕ виконати дію
"""
        
        return prompt
    
    def _get_fallback_coaching(self, current_score: int, target_score: int) -> Dict[str, Any]:
        """Fallback coaching if AI fails."""
        gap = target_score - current_score
        
        return {
            "priority_actions": [
                {
                    "action": "Додайте важливі терміни",
                    "impact": "high",
                    "difficulty": "easy",
                    "score_gain": f"+{min(gap // 2, 15)} балів",
                    "details": "Перевірте список термінів і додайте ті, що мають статус 'low'"
                },
                {
                    "action": "Додайте H2 заголовки",
                    "impact": "medium",
                    "difficulty": "easy",
                    "score_gain": "+5 балів",
                    "details": "Структуруйте контент за допомогою підзаголовків"
                }
            ],
            "content_suggestions": [
                "Розширте контент до рекомендованої довжини",
                "Додайте більше деталей та прикладів"
            ],
            "term_recommendations": {
                "add_more": [],
                "reduce": []
            },
            "changes": [
                {
                    "type": "add_term",
                    "term": "ключовий термін",
                    "location": "paragraph_1",
                    "old_text": "Це текст без термінів",
                    "new_text": "Це текст з ключовим терміном для покращення SEO",
                    "reason": "Додано важливий термін для покращення релевантності"
                },
                {
                    "type": "improve_heading",
                    "location": "h2_1",
                    "old_text": "Вступ",
                    "new_text": "Вступ до ключового терміну та його використання",
                    "reason": "Покращено заголовок додаванням ключових слів"
                }
            ],
            "revised_content": "",  # Will be filled by AI in real implementation
            "expected_score_gain": min(gap // 2, 15),
            "estimated_time": "30-45 хвилин"
        }


    def get_single_action(
        self,
        term_details: List[Dict[str, Any]],
        structure_details: Dict[str, Any],
        headings_details: Dict[str, Any],
        guidelines: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Get a single prioritized action to improve score.
        
        Args:
            term_details: Term analysis
            structure_details: Structure analysis
            headings_details: Headings analysis
            guidelines: Content guidelines
            
        Returns:
            Single action dict or None
        """
        actions = self.prioritize_actions(
            term_details,
            structure_details,
            headings_details,
            guidelines
        )
        return actions[0] if actions else None
    
    def prioritize_actions(
        self,
        term_details: List[Dict[str, Any]],
        structure_details: Dict[str, Any],
        headings_details: Dict[str, Any],
        guidelines: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Prioritize all possible actions by impact.
        
        Returns:
            Sorted list of actions (highest priority first)
        """
        actions = []
        
        # 1. Missing/low terms (highest priority)
        for term in term_details:
            if term.get('status') == 'low':
                needed = term['recommended_min'] - term['current']
                actions.append({
                    'type': 'add_term',
                    'priority': 1,
                    'impact': needed * 2,
                    'description': f"Додати термін '{term['term']}' {needed} раз(и)",
                    'details': f"Зараз: {term['current']}, норма: {term['recommended_min']}-{term['recommended_max']}",
                    'term': term['term'],
                    'count': needed
                })
        
        # 2. Over-optimized terms
        for term in term_details:
            if term.get('status') == 'high':
                excess = term['current'] - term['recommended_max']
                actions.append({
                    'type': 'reduce_term',
                    'priority': 2,
                    'impact': excess * 1.5,
                    'description': f"Зменшити термін '{term['term']}' на {excess} раз(и)",
                    'details': f"Зараз: {term['current']}, норма: {term['recommended_min']}-{term['recommended_max']}",
                    'term': term['term'],
                    'count': excess
                })
        
        # 3. Missing headings
        h2_h3_current = headings_details.get('h2_h3_count', {}).get('current', 0)
        h_min = guidelines.get('headings', {}).get('min', 3)
        
        if h2_h3_current < h_min:
            needed = h_min - h2_h3_current
            actions.append({
                'type': 'add_headings',
                'priority': 3,
                'impact': needed * 3,
                'description': f"Додати {needed} заголовк(ів) H2/H3",
                'details': f"Зараз: {h2_h3_current}, норма: {h_min}+",
                'count': needed
            })
        
        # 4. Word count
        wc_current = structure_details.get('word_count', {}).get('current', 0)
        wc_min = guidelines.get('word_count', {}).get('min', 800)
        
        if wc_current < wc_min:
            needed = wc_min - wc_current
            actions.append({
                'type': 'expand_content',
                'priority': 4,
                'impact': (needed / 100) * 2,
                'description': f"Розширити контент на {needed} слів",
                'details': f"Зараз: {wc_current}, норма: {wc_min}+",
                'count': needed
            })
        
        # Sort by priority (lower number = higher priority) and impact
        actions.sort(key=lambda x: (x['priority'], -x['impact']))
        
        return actions


# Convenience function
async def get_seo_coaching(
    current_score: int,
    target_score: int,
    breakdown: Dict[str, Any],
    term_details: List[Dict[str, Any]],
    structure_details: Optional[Dict[str, Any]] = None,
    headings_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate SEO coaching.
    
    Convenience wrapper around SEOCoach class.
    """
    coach = SEOCoach()
    return await coach.generate_coaching(
        current_score,
        target_score,
        breakdown,
        term_details,
        structure_details,
        headings_details
    )
