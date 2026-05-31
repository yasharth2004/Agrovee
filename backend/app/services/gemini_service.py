"""
Google Gemini API Service
Centralized service for Gemini text generation
Replaces local Ollama LLM with Google's Gemini 2.5 Flash
"""

import logging
import os
from typing import Optional
import time

from app.core.config import settings

logger = logging.getLogger(__name__)

# Try to import Google Generative AI
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    logger.warning("google-generativeai not installed - Gemini will be unavailable")


class GeminiService:
    """
    Service for text generation using Google Gemini API
    Handles initialization, error handling, retries, and timeouts
    """
    
    def __init__(self):
        """Initialize Gemini client with API key from environment"""
        self.api_key = os.getenv("GEMINI_API_KEY") or settings.GEMINI_API_KEY
        self.model = os.getenv("GEMINI_MODEL") or settings.GEMINI_MODEL
        self.client = None
        self.gemini_available = False

        if os.getenv("AGROVEE_DISABLE_GEMINI") == "1":
            logger.warning("AGROVEE_DISABLE_GEMINI=1 - Gemini will be unavailable")
            return
        
        if not self.api_key:
            logger.warning(
                "GEMINI_API_KEY not set in environment. "
                "Gemini will be unavailable. Set the environment variable to enable."
            )
            return
        
        if not GEMINI_AVAILABLE:
            logger.warning(
                "google-generativeai package not installed. "
                "Install it with: pip install google-generativeai"
            )
            return
        
        try:
            # Configure Gemini API
            genai.configure(api_key=self.api_key)
            self.client = genai.GenerativeModel(self.model)
            self.gemini_available = True
            logger.info(f"✓ Gemini configured — using model '{self.model}'")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini client: {e}")
            self.gemini_available = False

    def is_available(self) -> bool:
        """Check if Gemini is available and properly configured"""
        return self.gemini_available

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.5,
        top_p: float = 0.8,
        max_output_tokens: int = 200,
        timeout: int = 60,
        max_retries: int = 3
    ) -> Optional[str]:
        """
        Generate content using Gemini API
        
        Args:
            prompt: User prompt / question
            system_instruction: System prompt for context/behavior
            temperature: Controls randomness (0.0-1.0)
            top_p: Nucleus sampling parameter
            max_output_tokens: Maximum response length
            timeout: Request timeout in seconds
            max_retries: Number of retry attempts
            
        Returns:
            Generated text or None if failed
        """
        if not self.gemini_available:
            logger.error("Gemini is not available")
            return None
        
        if not self.client:
            logger.error("Gemini client not initialized")
            return None
        
        try:
            # Prepare generation config
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                top_p=top_p,
                max_output_tokens=max_output_tokens
            )
            
            # Prepare safety settings (allow agricultural/farming content)
            safety_settings = [
                {
                    "category": genai.types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
                    "threshold": genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                },
                {
                    "category": genai.types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
                    "threshold": genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                },
                {
                    "category": genai.types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                    "threshold": genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                },
                {
                    "category": genai.types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                    "threshold": genai.types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
                },
            ]
            
            model = self.client
            prompt_contents = prompt
            if system_instruction:
                try:
                    model = genai.GenerativeModel(
                        self.model,
                        system_instruction=system_instruction,
                    )
                except TypeError:
                    # Older SDK versions do not support system_instruction on
                    # the model. Keep Gemini usable by folding it into prompt.
                    prompt_contents = f"{system_instruction}\n\n{prompt}"

            # Retry logic for transient failures
            last_error = None
            for attempt in range(max_retries):
                try:
                    logger.debug(f"Gemini request attempt {attempt + 1}/{max_retries}")
                    
                    response = model.generate_content(
                        contents=prompt_contents,
                        generation_config=generation_config,
                        safety_settings=safety_settings,
                        request_options={"timeout": timeout}
                    )
                    
                    # Extract text from response
                    if response.text:
                        logger.info(f"Gemini response generated ({len(response.text)} chars)")
                        return response.text
                    else:
                        logger.warning(f"Gemini returned empty response (attempt {attempt + 1})")
                        if attempt < max_retries - 1:
                            time.sleep(1)  # Brief delay before retry
                            continue
                        return None
                
                except (TimeoutError, ConnectionError) as e:
                    last_error = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Timeout/connection error (attempt {attempt + 1}): {e}")
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        logger.error(f"Gemini request timeout after {max_retries} attempts")
                        return None
                
                except Exception as e:
                    last_error = e
                    if "RESOURCE_EXHAUSTED" in str(e):
                        logger.warning(f"Rate limited (attempt {attempt + 1}): {e}")
                        if attempt < max_retries - 1:
                            time.sleep(5 * (attempt + 1))  # Longer backoff for rate limiting
                            continue
                    logger.error(f"Gemini generation failed (attempt {attempt + 1}): {e}")
                    if attempt == max_retries - 1:
                        return None
                    time.sleep(1)
                    continue
            
            logger.error(f"All Gemini retry attempts exhausted: {last_error}")
            return None
        
        except Exception as e:
            logger.error(f"Unexpected error in Gemini generation: {e}")
            return None


# Global instance
_gemini_service = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service singleton"""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service
