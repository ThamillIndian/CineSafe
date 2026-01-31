"""
LLM client wrapper for Gemini API (using new google-genai SDK)
"""
from google import genai
from app.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import logging

logger = logging.getLogger(__name__)


class GeminiClient:
    """Wrapper for Google Gemini API calls (new genai SDK)"""
    
    def __init__(self):
        self.model = settings.gemini_model
        self.request_delay = settings.gemini_request_delay
        # Initialize client with API key (new SDK)
        self.client = genai.Client(api_key=settings.gemini_api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def call_model(self, prompt: str, temperature: float = 0.3) -> str:
        """
        Call Gemini model with retry logic (using new genai SDK)
        
        Args:
            prompt: The prompt text
            temperature: Temperature for generation (0.0-1.0)
        
        Returns:
            Model response text
        """
        try:
            # New SDK API: client.models.generate_content()
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=4096,
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise
    
    def extract_json_from_response(self, response_text: str) -> dict:
        """
        Extract JSON from LLM response
        
        Args:
            response_text: LLM response text
        
        Returns:
            Parsed JSON dict
        """
        try:
            # Try to find JSON in response
            start = response_text.find('{')
            end = response_text.rfind('}') + 1
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON from: {response_text}")
        
        return {}


# Global instance
gemini_client = GeminiClient()
