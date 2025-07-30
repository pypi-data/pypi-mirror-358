"""
HuggingFace provider integration.
"""

import logging
from typing import Dict, Any, List
import requests

from .base import BaseProvider
from ..types import ProviderType


logger = logging.getLogger(__name__)


class HuggingFaceProvider(BaseProvider):
    """HuggingFace API provider implementation."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize HuggingFace provider."""
        super().__init__(api_key, **kwargs)
        
        self.api_key = api_key
        self.api_url = "https://api-inference.huggingface.co/models/"
        
        # Default cost per 1K tokens (free tier)
        self.cost_per_1k_tokens = kwargs.get("cost_per_1k_tokens", 0.0)
        
        # Model-specific costs
        self.model_costs = {
            "gpt2": 0.0,
            "bert-base-uncased": 0.0,
            "t5-base": 0.0,
        }
        
        self.logger.info("Initialized HuggingFace provider")
    
    async def generate(
        self, 
        prompt: str, 
        model: str = "gpt2",
        **kwargs
    ) -> Dict[str, Any]:
        """Generate response using HuggingFace API."""
        await self._rate_limit()
        
        try:
            # Prepare headers
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare payload
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": kwargs.get("max_tokens", 100),
                    "temperature": kwargs.get("temperature", 0.7),
                    "top_p": kwargs.get("top_p", 1.0),
                    "do_sample": True,
                }
            }
            
            # Make API call
            response = requests.post(
                f"{self.api_url}{model}",
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            # Extract response
            result = response.json()
            text = result[0]["generated_text"] if isinstance(result, list) else result.get("generated_text", "")
            
            # Estimate token usage
            tokens_used = self._count_tokens(prompt) + self._count_tokens(text)
            
            return {
                "text": text,
                "tokens_used": tokens_used,
                "prompt_tokens": self._count_tokens(prompt),
                "completion_tokens": self._count_tokens(text),
                "model": model,
                "finish_reason": "STOP",
            }
            
        except Exception as e:
            self.logger.error(f"HuggingFace API error: {e}")
            raise
    
    def calculate_cost(self, tokens_used: int, model: str) -> float:
        """Calculate cost for HuggingFace API usage."""
        cost_per_1k = self.model_costs.get(model, self.cost_per_1k_tokens)
        return (tokens_used / 1000) * cost_per_1k
    
    def get_available_models(self) -> List[str]:
        """Get list of available HuggingFace models."""
        return [
            "gpt2",
            "bert-base-uncased",
            "t5-base",
            "microsoft/DialoGPT-medium",
            "EleutherAI/gpt-neo-125M",
        ]
    
    def get_provider_type(self) -> ProviderType:
        """Get provider type."""
        return ProviderType.HUGGINGFACE
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text (simple approximation).
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Approximate token count
        """
        # Simple approximation: 1 token ≈ 4 characters
        return len(text) // 4
    
    async def _rate_limit(self) -> None:
        """Apply rate limiting."""
        # Simple rate limiting - can be enhanced
        import asyncio
        await asyncio.sleep(0.1)  # 100ms delay 