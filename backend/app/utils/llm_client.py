"""
LLM client wrapper for Gemini API and Qwen3 Local (via LM Studio)
"""
from google import genai
from app.config import settings
from tenacity import retry, stop_after_attempt, wait_exponential
import json
import logging
import asyncio
import aiohttp

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


# ════════════════════════════════════════════════════════════════
# QWEN3 CLIENT: Local via LM Studio
# ════════════════════════════════════════════════════════════════

class Qwen3Client:
    """Local Qwen3 VI 4B client via LM Studio HTTP API"""
    
    def __init__(self, base_url: str = None, model: str = None):
        self.base_url = base_url or settings.qwen3_base_url
        self.model = model or settings.qwen3_model
        self.endpoint = f"{self.base_url}/chat/completions"
        logger.info(f"[Qwen3Client] Initialized at {self.endpoint}")
    
    async def call_model(self, prompt: str, temperature: float = 0.7, max_tokens: int = 4096) -> str:
        """
        Call Qwen3 model via LM Studio HTTP API
        
        Args:
            prompt: The prompt text
            temperature: Temperature for generation (0.0-1.0)
            max_tokens: Max tokens in response
        
        Returns:
            Model response text
        """
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert film production analyst. Provide detailed, structured analysis in valid JSON format."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "stream": False
                }
                
                async with session.post(
                    self.endpoint,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=120)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        logger.error(f"[Qwen3Client] HTTP {response.status}: {error_text}")
                        return ""
        
        except asyncio.TimeoutError:
            logger.error("[Qwen3Client] Request timeout (120s)")
            return ""
        except aiohttp.ClientConnectorError:
            logger.error("[Qwen3Client] Connection refused - is LM Studio running at " + self.endpoint + "?")
            return ""
        except Exception as e:
            logger.error(f"[Qwen3Client] Error: {str(e)}")
            return ""
    
    async def extract_json(self, prompt: str) -> list:
        """
        Call Qwen3 and extract JSON array from response
        
        Args:
            prompt: The prompt text
        
        Returns:
            Parsed JSON array
        """
        response_text = await self.call_model(prompt, temperature=0.3, max_tokens=8000)
        
        if not response_text:
            return []
        
        try:
            # Find JSON array in response
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            
            if start >= 0 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.warning(f"[Qwen3Client] JSON parse error: {e}")
        except Exception as e:
            logger.error(f"[Qwen3Client] Extraction error: {e}")
        
        return []

