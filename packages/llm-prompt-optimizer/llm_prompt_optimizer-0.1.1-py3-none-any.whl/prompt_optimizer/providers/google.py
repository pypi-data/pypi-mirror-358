"""
Google provider integration.
"""

import logging
from typing import Dict, Any, List
import google.generativeai as genai

from .base import BaseProvider
from ..types import ProviderType


logger = logging.getLogger(__name__)


class GoogleProvider(BaseProvider):
    """Google Generative AI provider implementation."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize Google provider."""
        super().__init__(api_key, **kwargs)
        
        # Set up Google client
        genai.configure(api_key=api_key)
        
        # Default cost per 1K tokens (Gemini Pro)
        self.cost_per_1k_tokens = kwargs.get("cost_per_1k_tokens", 0.0005)
        
        # Model-specific costs
        self.model_costs = {
            "gemini-pro": 0.0005,
            "gemini-pro-vision": 0.0005,
            "text-bison": 0.001,
            "chat-bison": 0.001,
        }
        
        self.logger.info("Initialized Google provider")
    
    async def generate(
        self, 
        prompt: str, 
        model: str = "gemini-pro",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using Google API."""
        await self._rate_limit()
        
        try:
            # Get model
            genai_model = genai.GenerativeModel(model)
            
            # Prepare parameters
            generation_config = {
                "max_output_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 1.0),
                "top_k": kwargs.get("top_k", 40),
            }
            
            # Make API call
            response = genai_model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract response
            text = response.text
            usage = response.usage_metadata
            
            return {
                "text": text,
                "tokens_used": usage.total_token_count if usage else 0,
                "prompt_tokens": usage.prompt_token_count if usage else 0,
                "completion_tokens": usage.candidates_token_count if usage else 0,
                "model": model,
                "finish_reason": "STOP",  # Google doesn't provide this
            }
            
        except Exception as e:
            self.logger.error(f"Google API error: {e}")
            raise
    
    def calculate_cost(self, tokens_used: int, model: str) -> float:
        """Calculate cost for Google API usage."""
        cost_per_1k = self.model_costs.get(model, self.cost_per_1k_tokens)
        return (tokens_used / 1000) * cost_per_1k
    
    def get_available_models(self) -> List[str]:
        """Get list of available Google models."""
        return [
            "gemini-pro",
            "gemini-pro-vision",
            "text-bison",
            "chat-bison",
        ]
    
    def get_provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.GOOGLE 