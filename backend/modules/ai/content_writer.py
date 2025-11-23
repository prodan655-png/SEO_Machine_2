"""
AI Content Writer Module.
Generates full HTML articles based on structured briefs.
"""

from typing import Dict, Any, Optional
from modules.ai.ai_client import get_ai_client
from logger import setup_logger

logger = setup_logger(__name__)


class ContentWriter:
    """AI-powered content writer."""
    
    def __init__(self):
        self.ai_client = get_ai_client()
    
    async def write_article(
        self,
        brief: Dict[str, Any],
        tone: str = "professional",
        language: str = "uk"
    ) -> str:
        """
        Write a full article based on the brief.
        
        Args:
            brief: Structured brief (JSON)
            tone: Content tone
            language: Content language
            
        Returns:
            HTML formatted article
        """
        try:
            prompt = self._build_prompt(brief, tone, language)
            
            # We need a longer response for full articles
            response = await self.ai_client.generate_content(
                prompt, 
                temperature=0.7,
                max_tokens=4000  # Increase token limit for full text
            )
            
            logger.info("Generated article content")
            return response
            
        except Exception as e:
            logger.error(f"Content writing failed: {str(e)}")
            raise

    def _build_prompt(
        self,
        brief: Dict[str, Any],
        tone: str,
        language: str
    ) -> str:
        """Build the prompt for writing."""
        
        # Convert brief to string representation
        import json
        brief_str = json.dumps(brief, ensure_ascii=False, indent=2)
        
        prompt = f"""Ти професійний копірайтер. Твоє завдання - написати повну статтю на основі наданого брифу.

МОВА: {language}
ТОН: {tone}

БРИФ (СТРУКТУРА):
{brief_str}

ВИМОГИ ДО КОНТЕНТУ:
1. Пиши цікаво, експертно і для людей.
2. Використовуй HTML теги для форматування:
   - <h1> для головного заголовку (тільки один)
   - <h2>, <h3> для підзаголовків
   - <p> для абзаців
   - <ul>, <ol>, <li> для списків
   - <strong>, <em> для акцентів
3. Не використовуй <html>, <head>, <body> теги - тільки контент.
4. Розкривай кожен пункт брифу детально.
5. Органічно вписуй рекомендовані терміни.

ВАЖЛИВО:
- Текст має бути унікальним.
- Уникай "води" і загальних фраз.
- Довжина має відповідати оцінці в брифі.

Починай писати одразу HTML код статті:
"""
        return prompt


async def write_article(
    brief: Dict[str, Any],
    tone: str = "professional",
    language: str = "uk"
) -> str:
    """Convenience wrapper for ContentWriter."""
    writer = ContentWriter()
    return await writer.write_article(brief, tone, language)
