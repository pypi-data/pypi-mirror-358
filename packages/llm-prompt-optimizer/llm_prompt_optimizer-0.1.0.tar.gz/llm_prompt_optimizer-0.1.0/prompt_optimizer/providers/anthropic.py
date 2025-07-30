"""
Anthropic provider integration.
"""

import logging
from typing import Dict, Any, List
import anthropic

from .base import BaseProvider
from ..types import ProviderType


logger = logging.getLogger(__name__)


class AnthropicProvider(BaseProvider):
    """Anthropic API provider implementation."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize Anthropic provider."""
        super().__init__(api_key, **kwargs)
        
        # Set up Anthropic client
        self.client = anthropic.Anthropic(api_key=api_key)
        
        # Default cost per 1K tokens (Claude-3-Sonnet)
        self.cost_per_1k_tokens = kwargs.get("cost_per_1k_tokens", 0.003)
        
        # Model-specific costs
        self.model_costs = {
            "claude-3-haiku": 0.00025,
            "claude-3-sonnet": 0.003,
            "claude-3-opus": 0.015,
            "claude-2.1": 0.008,
            "claude-2.0": 0.008,
        }
        
        self.logger.info("Initialized Anthropic provider")
    
    async def generate(
        self, 
        prompt: str, 
        model: str = "claude-3-sonnet",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using Anthropic API."""
        await self._rate_limit()
        
        try:
            # Prepare parameters
            params = {
                "model": model,
                "max_tokens": kwargs.get("max_tokens", 1000),
                "temperature": kwargs.get("temperature", 0.7),
                "top_p": kwargs.get("top_p", 1.0),
                "top_k": kwargs.get("top_k", 40),
            }
            
            # Make API call
            response = self.client.messages.create(
                messages=[{"role": "user", "content": prompt}],
                **params
            )
            
            # Extract response
            text = response.content[0].text
            usage = response.usage
            
            return {
                "text": text,
                "tokens_used": usage.input_tokens + usage.output_tokens,
                "prompt_tokens": usage.input_tokens,
                "completion_tokens": usage.output_tokens,
                "model": model,
                "finish_reason": response.stop_reason,
            }
            
        except Exception as e:
            self.logger.error(f"Anthropic API error: {e}")
            raise
    
    def calculate_cost(self, tokens_used: int, model: str) -> float:
        """Calculate cost for Anthropic API usage."""
        cost_per_1k = self.model_costs.get(model, self.cost_per_1k_tokens)
        return (tokens_used / 1000) * cost_per_1k
    
    def get_available_models(self) -> List[str]:
        """Get list of available Anthropic models."""
        return [
            "claude-3-haiku",
            "claude-3-sonnet",
            "claude-3-opus",
            "claude-2.1",
            "claude-2.0",
        ]
    
    def get_provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.ANTHROPIC 