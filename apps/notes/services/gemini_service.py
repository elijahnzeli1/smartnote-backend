"""
Gemini AI service for generating note summaries.
"""
import logging
import time
from typing import Optional
import google.generativeai as genai
from django.conf import settings
from core.exceptions import AIServiceException

logger = logging.getLogger(__name__)


class GeminiSummarizer:
    """
    Service class for generating AI summaries using Google Gemini.
    """
    
    def __init__(self):
        """
        Initialize the Gemini API client.
        """
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.max_retries = settings.GEMINI_MAX_RETRIES
        self.timeout = settings.GEMINI_TIMEOUT
        
        if not self.api_key:
            logger.warning("Gemini API key not configured")
        else:
            genai.configure(api_key=self.api_key)
    
    def generate_summary(self, content: str, max_length: int = 150) -> str:
        """
        Generate a summary for the given content using Gemini AI.
        
        Args:
            content: The text content to summarize
            max_length: Maximum length of the summary in words
            
        Returns:
            Generated summary text
            
        Raises:
            AIServiceException: If summary generation fails
        """
        if not self.api_key:
            raise AIServiceException(
                "Gemini API key not configured",
                details="Please set GOOGLE_API_KEY in environment variables"
            )
        
        if not content or len(content.strip()) == 0:
            raise AIServiceException(
                "Cannot summarize empty content",
                details="Content must not be empty"
            )
        
        # For very short content, return as-is or truncate
        if len(content.split()) <= 20:
            return content[:max_length * 5]  # Approximate character length
        
        prompt = self._build_prompt(content, max_length)
        
        # Retry logic with exponential backoff
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Generating summary (attempt {attempt + 1}/{self.max_retries})")
                summary = self._call_gemini_api(prompt)
                logger.info("Summary generated successfully")
                return summary
                
            except Exception as e:
                logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    # Exponential backoff: wait 1s, 2s, 4s...
                    wait_time = 2 ** attempt
                    logger.info(f"Retrying in {wait_time} seconds...")
                    time.sleep(wait_time)
                else:
                    # All retries failed
                    logger.error("All retry attempts failed", exc_info=True)
                    raise AIServiceException(
                        "Failed to generate summary after retries",
                        details=str(e)
                    )
        
        # Fallback: extractive summary
        return self._extractive_summary(content, max_length)
    
    def _build_prompt(self, content: str, max_length: int) -> str:
        """
        Build the prompt for Gemini API.
        """
        return f"""Summarize the following note in approximately {max_length} words or less. 
Make it concise, clear, and capture the key points. Do not include any preamble or 
explanation - just provide the summary.

Note content:
{content}

Summary:"""
    
    def _call_gemini_api(self, prompt: str) -> str:
        """
        Make the actual API call to Gemini.
        """
        try:
            model = genai.GenerativeModel(self.model_name)
            
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more focused summaries
                    max_output_tokens=200,
                )
            )
            
            if not response or not response.text:
                raise AIServiceException("Empty response from Gemini API")
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            raise
    
    def _extractive_summary(self, content: str, max_length: int) -> str:
        """
        Fallback extractive summary - returns first N words.
        """
        logger.info("Using extractive summary as fallback")
        words = content.split()
        summary_words = words[:max_length]
        summary = ' '.join(summary_words)
        
        if len(words) > max_length:
            summary += '...'
        
        return summary


# Singleton instance
_summarizer_instance = None


def get_summarizer() -> GeminiSummarizer:
    """
    Get or create a singleton instance of GeminiSummarizer.
    """
    global _summarizer_instance
    if _summarizer_instance is None:
        _summarizer_instance = GeminiSummarizer()
    return _summarizer_instance
