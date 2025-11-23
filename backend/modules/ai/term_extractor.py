"""
AI-powered Term Extractor.
Uses Gemini AI to extract semantic key terms from competitor content.
"""

from typing import List, Dict, Any
from modules.ai.ai_client import get_ai_client
from logger import setup_logger
import json

logger = setup_logger(__name__)


async def extract_terms_with_ai(
    competitors_texts: List[str],
    keyword: str,
    language: str,
    max_terms: int = 20
) -> List[Dict[str, Any]]:
    """
    Extract key terms using AI semantic analysis.
    
    Args:
        competitors_texts: List of competitor content texts
        keyword: Main keyword being analyzed
        language: Language code (uk, en)
        max_terms: Maximum number of terms to extract
        
    Returns:
        List of term dicts with recommendations
    """
    if not competitors_texts:
        logger.warning("No competitor texts provided for AI term extraction")
        return []
    
    # Combine texts (limit to avoid token limits)
    combined_text = "\n\n---COMPETITOR---\n\n".join(competitors_texts[:5])
    # Limit total length
    combined_text = combined_text[:8000]
    
    prompt = f"""Ти експерт з SEO та семантичного аналізу контенту.

ЗАВДАННЯ: Проаналізуй тексти конкурентів для ключового слова "{keyword}" та витягни найважливіші семантичні терміни.

ТЕКСТИ КОНКУРЕНТІВ:
{combined_text}

ПРАВИЛА:
1. Витягни {max_terms} найважливіших термінів
2. НЕ включай стоп-слова (на, як, що, та, з, в, і, це, не тощо)
3. Терміни мають бути РЕЛЕВАНТНІ до теми "{keyword}"
4. Включи:
   - Однослівні терміни (іменники, дієслова)
   - Двослівні фрази (важливі словосполучення)
   - Синоніми основного ключа
5. Для кожного терміну визнач рекомендовану частоту використання (min, max)

ФОРМАТ ВІДПОВІДІ (JSON):
{{
  "terms": [
    {{
      "term": "назва терміну",
      "type": "phrase" або "keyword",
      "min_recommended": мінімальна частота,
      "max_recommended": максимальна частота,
      "relevance": "пояснення чому цей термін важливий"
    }}
  ]
}}

ПРИКЛАД для "торт рецепт":
{{
  "terms": [
    {{"term": "торт", "type": "keyword", "min_recommended": 8, "max_recommended": 15, "relevance": "основний термін"}},
    {{"term": "рецепт", "type": "keyword", "min_recommended": 6, "max_recommended": 12, "relevance": "основний термін"}},
    {{"term": "випічка", "type": "phrase", "min_recommended": 3, "max_recommended": 6, "relevance": "категорія"}}
  ]
}}

Поверни ТІЛЬКИ JSON, без додаткового тексту.
"""
    
    try:
        ai_client = get_ai_client()
        logger.info(f"Extracting terms with AI for keyword '{keyword}'")
        
        response = await ai_client.generate_content(
            prompt,
            temperature=0.3,  # Lower temperature for more consistent results
            max_tokens=2000
        )
        
        # Parse JSON response
        response_text = response.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        result = json.loads(response_text)
        terms = result.get('terms', [])
        
        # Format for compatibility with existing system
        formatted_terms = []
        for term_data in terms:
            formatted_terms.append({
                'term': term_data['term'],
                'term_normalized': term_data['term'].lower(),
                'type': term_data.get('type', 'phrase'),
                'min_recommended': term_data.get('min_recommended', 3),
                'max_recommended': term_data.get('max_recommended', 8),
                'avg_in_competitors': (term_data.get('min_recommended', 3) + term_data.get('max_recommended', 8)) / 2,
                'median_in_competitors': (term_data.get('min_recommended', 3) + term_data.get('max_recommended', 8)) / 2,
                'docs_used_in': len(competitors_texts),
                'occurrences_by_position': [],
                'ai_relevance': term_data.get('relevance', '')
            })
        
        logger.info(f"AI extracted {len(formatted_terms)} terms")
        return formatted_terms
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AI response as JSON: {e}")
        logger.error(f"Response was: {response_text[:500]}")
        return []
    except Exception as e:
        logger.error(f"AI term extraction failed: {e}", exc_info=True)
        return []
