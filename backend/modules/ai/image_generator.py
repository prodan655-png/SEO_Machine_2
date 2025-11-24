"""
AI Image Generator Module.
Generates relevant images for article content using Gemini Imagen.
"""

import os
import base64
from typing import List, Dict, Any
from pathlib import Path
import google.generativeai as genai
from bs4 import BeautifulSoup
from logger import setup_logger

logger = setup_logger(__name__)


class ImageGenerator:
    """AI-powered image generator for article content."""
    
    def __init__(self):
        """Initialize Image Generator."""
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('AI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.enabled = True
            logger.info("Image generator initialized")
        else:
            self.enabled = False
            logger.warning("Image generation disabled - no API key")
    
    def extract_sections(self, html_content: str) -> List[Dict[str, Any]]:
        """
        Extract main sections from HTML content.
        
        Args:
            html_content: HTML string
            
        Returns:
            List of sections with titles and positions
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        sections = []
        
        # Find all h2 and h3 headings
        headings = soup.find_all(['h2', 'h3'])
        
        for idx, heading in enumerate(headings):
            sections.append({
                'index': idx,
                'title': heading.get_text(strip=True),
                'level': heading.name,
                'element': heading
            })
        
        return sections
    
    def generate_prompts(
        self, 
        sections: List[Dict[str, Any]], 
        keyword: str,
        num_images: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate image prompts for sections.
        
        Args:
            sections: List of extracted sections
            keyword: Main article keyword
            num_images: Number of images to generate
            
        Returns:
            List of prompt dicts
        """
        prompts = []
        
        # Select top sections (evenly distributed)
        selected_indices = self._select_section_indices(len(sections), num_images)
        
        for i, section_idx in enumerate(selected_indices):
            if section_idx < len(sections):
                section = sections[section_idx]
                
                prompt = self._create_image_prompt(
                    keyword=keyword,
                    section_title=section['title'],
                    section_index=i + 1,
                    total_images=num_images
                )
                
                prompts.append({
                    'section_index': section['index'],
                    'heading': section['title'],
                    'prompt': prompt
                })
        
        return prompts
    
    def _select_section_indices(self, total_sections: int, num_images: int) -> List[int]:
        """Select evenly distributed section indices."""
        if total_sections == 0:
            return []
        
        if num_images >= total_sections:
            return list(range(total_sections))
        
        # Evenly distribute
        step = total_sections / num_images
        return [int(i * step) for i in range(num_images)]
    
    def _create_image_prompt(
        self,
        keyword: str,
        section_title: str,
        section_index: int,
        total_images: int
    ) -> str:
        """Create image generation prompt."""
        return f"""Create a professional, modern, high-quality illustration for an article about '{keyword}'.

Section: {section_title}
Style: Clean, minimalist, web-friendly
Theme: Educational and informative
Colors: Vibrant but professional
Format: 16:9 aspect ratio

The image should:
- Clearly relate to '{keyword}' and '{section_title}'
- Be suitable for a web article
- Have a modern, clean design
- Use professional illustration style (not photorealistic)
- Include relevant icons or visual metaphors
- Be visually appealing and engaging

Avoid: Text, watermarks, overly complex details, stock photo look"""
    
    async def generate_article_images(
        self,
        article_html: str,
        keyword: str,
        num_images: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate images for article sections.
        
        Args:
            article_html: HTML content of article
            keyword: Main keyword
            num_images: Number of images to generate (1-5)
            
        Returns:
            List of image dicts with URLs and metadata
        """
        if not self.enabled:
            logger.warning("Image generation called but not enabled")
            return self._get_placeholder_images(num_images)
        
        try:
            # Extract sections
            sections = self.extract_sections(article_html)
            if not sections:
                logger.info("No sections found in HTML")
                return []
            
            # Generate prompts
            prompts = self.generate_prompts(sections, keyword, num_images)
            
            # Generate images
            images = []
            for i, prompt_data in enumerate(prompts):
                logger.info(f"Generating image {i+1}/{len(prompts)}")
                
                # Note: Imagen API integration would go here
                # For now, return placeholder data
                image_url = self._generate_placeholder_url(i)
                
                images.append({
                    'section_index': prompt_data['section_index'],
                    'image_url': image_url,
                    'alt_text': f"Illustration for {prompt_data['heading']}",
                    'caption': prompt_data['heading'],
                    'prompt': prompt_data['prompt']
                })
            
            logger.info(f"Generated {len(images)} images")
            return images
            
        except Exception as e:
            logger.error(f"Image generation failed: {str(e)}")
            return self._get_placeholder_images(num_images)
    
    def _generate_placeholder_url(self, index: int) -> str:
        """Generate placeholder image URL."""
        # Use a placeholder service
        colors = ['3b82f6', '10b981', 'f59e0b', 'ef4444', '8b5cf6']
        color = colors[index % len(colors)]
        return f"https://placehold.co/800x450/{color}/ffffff?text=Image+{index+1}"
    
    def _get_placeholder_images(self, num_images: int) -> List[Dict[str, Any]]:
        """Get placeholder images when generation is not available."""
        return [
            {
                'section_index': i,
                'image_url': self._generate_placeholder_url(i),
                'alt_text': f'Article illustration {i+1}',
                'caption': f'Image {i+1}',
                'prompt': ''
            }
            for i in range(num_images)
        ]


def insert_images_into_html(html_content: str, images: List[Dict[str, Any]]) -> str:
    """
    Insert generated images into HTML content.
    
    Args:
        html_content: Original HTML
        images: List of image dicts from generate_article_images
        
    Returns:
        HTML with images inserted
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    headings = soup.find_all(['h2', 'h3'])
    
    for img_data in images:
        section_idx = img_data['section_index']
        
        if section_idx < len(headings):
            heading = headings[section_idx]
            
            # Create figure element
            figure = soup.new_tag('figure', **{'class': 'article-image'})
            
            # Create img element
            img = soup.new_tag(
                'img',
                src=img_data['image_url'],
                alt=img_data['alt_text'],
                loading='lazy'
            )
            figure.append(img)
            
            # Add caption if provided
            if img_data.get('caption'):
                figcaption = soup.new_tag('figcaption')
                figcaption.string = img_data['caption']
                figure.append(figcaption)
            
            # Insert after heading
            heading.insert_after(figure)
    
    return str(soup)


# Convenience function
async def generate_article_images(
    article_html: str,
    keyword: str,
    num_images: int = 3
) -> List[Dict[str, Any]]:
    """
    Generate images for article.
    
    Convenience wrapper around ImageGenerator class.
    """
    generator = ImageGenerator()
    return await generator.generate_article_images(article_html, keyword, num_images)
