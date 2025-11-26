"""
AI Brief Generator Module.
Generates structured content briefs based on SEO analysis data.
"""

from typing import Dict, Any, List, Optional
from modules.ai.ai_client import get_ai_client
from logger import setup_logger

logger = setup_logger(__name__)


class BriefGenerator:
    """AI-powered content brief generator."""
    
    def __init__(self):
        self.ai_client = get_ai_client()
    
    async def generate_brief(
        self,
        keyword: str,
        language: str,
        competitors_data: List[Dict[str, Any]],
        terms_data: List[Dict[str, Any]],
        guidelines: Optional[Dict[str, Any]] = None,
        project_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a content brief.
        
        Args:
            keyword: Target keyword
            language: Content language
            competitors_data: List of competitor analysis results
            terms_data: List of important terms
            guidelines: Structural guidelines (word count, etc.)
            
        Returns:
            Structured brief (JSON)
        """
        try:
            prompt = self._build_prompt(
                keyword, language, competitors_data, terms_data, guidelines, project_context
            )
            
            response = await self.ai_client.generate_json(prompt, temperature=0.7)
            
            logger.info(f"Generated brief for '{keyword}'")
            return response
            
        except Exception as e:
            logger.error(f"Brief generation failed: {str(e)}")
            raise

    def _build_prompt(
        self,
        keyword: str,
        language: str,
        competitors_data: List[Dict[str, Any]],
        terms_data: List[Dict[str, Any]],
        guidelines: Optional[Dict[str, Any]],
        project_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build the prompt for brief generation."""
        
        # Extract top headings from competitors
        all_headings = []
        for comp in competitors_data[:5]:  # Top 5 competitors
            headings = comp.get('extracted_data', {}).get('headings', [])
            # Filter only H2 and H3
            filtered = [h['text'] for h in headings if h['level'] in ['h2', 'h3']]
            all_headings.extend(filtered[:5])  # Take top 5 from each
        
        competitor_structure = "\n".join([f"- {h}" for h in all_headings[:15]])
        
        # Extract top terms
        top_terms = [t['term'] for t in terms_data[:10]]
        terms_list = ", ".join(top_terms)
        
        # Guidelines
        wc_min = guidelines.get('word_count', {}).get('min', 800) if guidelines else 800
        wc_max = guidelines.get('word_count', {}).get('max', 1500) if guidelines else 1500
        
        context_note = ""
        if project_context and project_context.get('description'):
            context_note = f"""\n!!! КОНТЕКСТ БРЕНДУ/ПРОЕКТУ !!!
{project_context.get('description')}
Цільова аудиторія: {project_context.get('target_audience', 'не вказана')}
!!! КІНЕЦЬ КОНТЕКСТУ !!!
"""
        
        prompt = f"""Ти професійний SEO-стратег. Твоє завдання - створити детальний бриф (структуру) для статті.

КЛЮЧОВЕ СЛОВО: {keyword}
МОВА: {language}
{context_note}
ВАЖЛИВО: ПРОАНАЛІЗУЙ ІНТЕНТ (НАМІР) КОРИСТУВАЧА!
Подивись на заголовки конкурентів нижче. Якщо вони пишуть про конкретний бренд, продукт або специфічну нішу - твій бриф МАЄ відповідати цьому контексту.
Якщо є КОНТЕКСТ БРЕНДУ/ПРОЕКТУ вище - використовуй його як ПРІОРИТЕТНИЙ контекст!

КОНКУРЕНТИ ВИКОРИСТОВУЮТЬ ТАКІ ЗАГОЛОВКИ:
{competitor_structure}

ВАЖЛИВІ ТЕРМІНИ (LSI):
{terms_list}

ВИМОГИ:
- Обсяг: {wc_min}-{wc_max} слів
- Цільова аудиторія: широка, зацікавлена в темі
- Тон: експертний, але зрозумілий

ЗАВДАННЯ:
Створи JSON структуру статті.

ФОРМАТ ВІДПОВІДІ (JSON):
{{
    "title_options": ["Заголовок 1", "Заголовок 2", "Заголовок 3"],
    "meta_description": "Оптимізований опис до 160 символів...",
    "structure": [
        {{
            "heading": "Назва H2 заголовку",
            "level": "h2",
            "key_points": ["теза 1", "теза 2"],
            "recommended_terms": ["термін1", "термін2"]
        }},
        {{
            "heading": "Назва наступного H2",
            "level": "h2",
            "subsections": [
                {{
                    "heading": "Назва H3",
                    "level": "h3",
                    "key_points": ["..."]
                }}
            ]
        }}
    ],
    "estimated_word_count": 1200
}}

ПРАВИЛА:
1. Структура має бути логічною і повною.
2. Використовуй українську мову (або мову запиту).
3. Заголовки мають бути привабливими (click-worthy).
4. Обов'язково включи в структуру використання важливих термінів.
"""
        return prompt


async def generate_brief(
    keyword: str,
    language: str,
    competitors_data: List[Dict[str, Any]],
    terms_data: List[Dict[str, Any]],
    guidelines: Optional[Dict[str, Any]] = None,
    project_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Convenience wrapper for BriefGenerator."""
    generator = BriefGenerator()
    return await generator.generate_brief(
        keyword, language, competitors_data, terms_data, guidelines, project_context
    )
