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
        language: str = "uk",
        improvement_instructions: Optional[str] = None
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
            prompt = self._build_prompt(brief, tone, language, improvement_instructions)
            
            # We need a longer response for full articles
            response = await self.ai_client.generate_content(
                prompt, 
                temperature=0.7,
                max_tokens=4000  # Increase token limit for full text
            )
            
            logger.info("Generated article content")
            
            # Clean markdown artifacts
            content = response
            if content.startswith('```html'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]
            
            return content.strip()
            
        except Exception as e:
            logger.error(f"Content writing failed: {str(e)}")
            raise

    def _build_prompt(
        self,
        brief: Dict[str, Any],
        tone: str,
        language: str,
        improvement_instructions: Optional[str] = None
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
"""
        if improvement_instructions:
            prompt += f"""
!!! ВАЖЛИВО: ІНСТРУКЦІЇ ДЛЯ ПОКРАЩЕННЯ (SEO COACH) !!!
Ти повинен суворо дотримуватися цих рекомендацій, щоб підвищити SEO оцінку статті:
{improvement_instructions}
!!! КІНЕЦЬ ІНСТРУКЦІЙ !!!
"""

        prompt += """
Починай писати одразу HTML код статті:
"""
        
        logger.info(f"📝 AI PROMPT (Coach Instructions included: {bool(improvement_instructions)})")
        if improvement_instructions:
            logger.info(f"Coach Instructions:\n{improvement_instructions}")
        
        return prompt

    async def edit_content(
        self,
        current_content: str,
        action: Dict[str, Any],
        language: str = "uk"
    ) -> str:
        """
        Edit existing content with a single specific change.
        
        Args:
            current_content: Current HTML content
            action: Action to apply (from Coach)
            language: Content language
            
        Returns:
            Edited HTML content
        """
        prompt = self._build_edit_prompt(current_content, action, language)
        
        try:
            response = await self.ai_client.generate_content(
                prompt,
                temperature=0.5,
                max_tokens=8000
            )
            
            # Clean markdown artifacts
            import re
            response = re.sub(r'^```html\s*', '', response, flags=re.MULTILINE)
            response = re.sub(r'\s*```$', '', response, flags=re.MULTILINE)
            response = response.strip()
            
            logger.info(f"Edited content with action: {action.get('description', 'unknown')}")
            return response
            
        except Exception as e:
            logger.error(f"Content editing failed: {str(e)}")
            raise
    
    def _build_edit_prompt(
        self,
        current_content: str,
        action: Dict[str, Any],
        language: str
    ) -> str:
        """
        Build prompt for editing content.
        
        Args:
            current_content: Current content
            action: Action to apply
            language: Content language
            
        Returns:
            Prompt string
        """
        action_desc = action.get('description', '')
        action_details = action.get('details', '')
        
        prompt = f"""
Ти професійний редактор контенту. Твоє завдання - зробити ОДНУ конкретну зміну в тексті.

ПОТОЧНИЙ КОНТЕНТ:
{current_content}

ЗАВДАННЯ:
{action_desc}

ДЕТАЛІ:
{action_details}

ПРАВИЛА:
1. Зроби ТІЛЬКИ цю одну зміну
2. НЕ видаляй існуючий контент
3. НЕ змінюй структуру без необхідності  
4. Зберігай стиль і тон оригіналу
5. Інтегруй зміни природньо в текст
6. Використовуй мову: {language}

Поверни ПОВНИЙ оновлений HTML контент (без ```html тегів):
"""
        return prompt


async def write_article(
    brief: Dict[str, Any],
    tone: str = "professional",
    language: str = "uk",
    improvement_instructions: Optional[str] = None
) -> str:
    """Convenience wrapper for ContentWriter."""
    writer = ContentWriter()
    return await writer.write_article(brief, tone, language, improvement_instructions)
