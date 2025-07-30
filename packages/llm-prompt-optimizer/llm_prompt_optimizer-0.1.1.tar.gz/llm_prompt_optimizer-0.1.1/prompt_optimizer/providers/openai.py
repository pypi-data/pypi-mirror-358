"""
OpenAI provider integration.
"""

import logging
from typing import Dict, Any, List
import openai

from .base import BaseProvider
from ..types import ProviderType


logger = logging.getLogger(__name__)


class OpenAIProvider(BaseProvider):
    """OpenAI API provider implementation."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize OpenAI provider."""
        super().__init__(api_key, **kwargs)
        
        # Set up OpenAI client
        openai.api_key = api_key
        
        # Default cost per 1K tokens (GPT-3.5-turbo)
        self.cost_per_1k_tokens = kwargs.get("cost_per_1k_tokens", 0.002)
        
        # Model-specific costs
        self.model_costs = {
            "gpt-3.5-turbo": 0.002,
            "gpt-3.5-turbo-16k": 0.003,
            "gpt-4": 0.03,
            "gpt-4-turbo": 0.01,
            "gpt-4-32k": 0.06,
        }
        
        self.logger.info("Initialized OpenAI provider")
    
    async def generate(
        self, 
        prompt: str, 
        model: str = "gpt-3.5-turbo",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using OpenAI API."""
        await self._rate_limit()
        
        try:
            # Prepare parameters
            params = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 1.0),
                "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
                "presence_penalty": kwargs.get("presence_penalty", 0.0),
            }
            
            # Make API call
            response = await openai.ChatCompletion.acreate(**params)
            
            # Extract response
            text = response.choices[0].message.content
            usage = response.usage
            
            return {
                "text": text,
                "tokens_used": usage.total_tokens,
                "prompt_tokens": usage.prompt_tokens,
                "completion_tokens": usage.completion_tokens,
                "model": model,
                "finish_reason": response.choices[0].finish_reason,
            }
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise
    
    def calculate_cost(self, tokens_used: int, model: str) -> float:
        """Calculate cost for OpenAI API usage."""
        cost_per_1k = self.model_costs.get(model, self.cost_per_1k_tokens)
        return (tokens_used / 1000) * cost_per_1k
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models."""
        return [
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k", 
            "gpt-4",
            "gpt-4-turbo",
            "gpt-4-32k",
        ]
    
    def get_provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.OPENAI
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens using OpenAI's tokenizer."""
        try:
            # Use OpenAI's tokenizer if available
            import tiktoken
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return len(encoding.encode(text))
        except ImportError:
            # Fallback to basic counting
            return super()._count_tokens(text) 