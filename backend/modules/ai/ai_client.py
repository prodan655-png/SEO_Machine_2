"""
Google Gemini AI Client.
Wrapper for Google's Generative AI API.
"""

import os
from typing import Optional, Dict, Any
import json
import google.generativeai as genai
from logger import setup_logger
from config import get_config

logger = setup_logger(__name__)


class GeminiClient:
    """Client for Google Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            api_key: Google AI API key (optional, reads from env)
        """
        self.api_key = api_key or get_config('ai.gemini_api_key') or os.getenv('GEMINI_API_KEY')
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in config or environment")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Model settings - Gemini 2.0
        self.model_name = get_config('ai.model', 'gemini-2.0-flash')
        self.temperature = get_config('ai.temperature', 0.7)
        self.max_tokens = get_config('ai.max_tokens', 2000)
        
        logger.info(f"Gemini client initialized with model: {self.model_name}")
    
    async def generate_content(
        self,
        prompt: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """
        Generate content from prompt.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text
            
        Raises:
            Exception: If API call fails
        """
        try:
            model = genai.GenerativeModel(self.model_name)
            
            generation_config = genai.types.GenerationConfig(
                temperature=temperature or self.temperature,
                max_output_tokens=max_tokens or self.max_tokens
            )
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract text from response
            if response and response.text:
                logger.info(f"Generated {len(response.text)} characters")
                return response.text
            else:
                raise Exception("Empty response from Gemini")
                
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    async def generate_json(
        self,
        prompt: str,
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate structured JSON output.
        
        Args:
            prompt: Input prompt (should request JSON output)
            temperature: Sampling temperature
            
        Returns:
            Parsed JSON dict
            
        Raises:
            Exception: If API call fails or JSON parsing fails
        """
        try:
            # Request JSON explicitly
            json_prompt = f"{prompt}\n\nВІДПОВІДЬ ТІЛЬКИ У ФОРМАТІ JSON, БЕЗ MARKDOWN:"
            
            text = await self.generate_content(json_prompt, temperature)
            
            # Clean markdown if present
            text = text.strip()
            if text.startswith('```json'):
                text = text[7:]
            if text.startswith('```'):
                text = text[3:]
            if text.endswith('```'):
                text = text[:-3]
            text = text.strip()
            
            # Parse JSON
            result = json.loads(text)
            logger.info("Successfully parsed JSON response")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error: {str(e)}\nRaw text: {text[:200]}")
            raise Exception(f"Failed to parse JSON response: {str(e)}")
        except Exception as e:
            logger.error(f"JSON generation error: {str(e)}")
            raise
    
    def is_available(self) -> bool:
        """Check if AI client is properly configured."""
        return bool(self.api_key)


# Singleton instance
_client: Optional[GeminiClient] = None


def get_ai_client() -> GeminiClient:
    """Get or create Gemini client instance."""
    global _client
    
    if not get_config('ai.enabled', False):
        raise Exception("AI features are disabled in config")
    
    if _client is None:
        _client = GeminiClient()
    
    return _client
