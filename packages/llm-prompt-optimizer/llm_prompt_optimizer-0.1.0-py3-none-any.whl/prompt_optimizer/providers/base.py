"""
Base provider interface for LLM integrations.
"""

import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime

from ..types import ProviderType


logger = logging.getLogger(__name__)


class BaseProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    All provider implementations must inherit from this class
    and implement the required methods.
    """
    
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the provider.
        
        Args:
            api_key: API key for the provider
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Rate limiting
        self.rate_limit = kwargs.get("rate_limit", 100)  # requests per minute
        self.last_request_time = 0
        
        # Cost tracking
        self.cost_per_1k_tokens = kwargs.get("cost_per_1k_tokens", 0.0)
    
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        model: str = "default",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generate a response from the LLM.
        
        Args:
            prompt: Input prompt
            model: Model name to use
            **kwargs: Additional generation parameters
            
        Returns:
            Dictionary containing response text and metadata
        """
        pass
    
    @abstractmethod
    def calculate_cost(self, tokens_used: int, model: str) -> float:
        """
        Calculate the cost for a given number of tokens.
        
        Args:
            tokens_used: Number of tokens used
            model: Model name
            
        Returns:
            Cost in USD
        """
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """
        Get list of available models for this provider.
        
        Returns:
            List of model names
        """
        pass
    
    @abstractmethod
    def get_provider_type(self) -> ProviderType:
        """
        Get the provider type.
        
        Returns:
            ProviderType enum value
        """
        pass
    
    async def _rate_limit(self) -> None:
        """Implement rate limiting."""
        current_time = datetime.utcnow().timestamp()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < (60.0 / self.rate_limit):
            sleep_time = (60.0 / self.rate_limit) - time_since_last
            await asyncio.sleep(sleep_time)
        
        self.last_request_time = datetime.utcnow().timestamp()
    
    def _count_tokens(self, text: str) -> int:
        """
        Count tokens in text (basic implementation).
        
        Args:
            text: Text to count tokens for
            
        Returns:
            Approximate token count
        """
        # Basic token counting (words + punctuation)
        # Providers should override this with their specific tokenizer
        return len(text.split()) + len([c for c in text if c in '.,!?;:'])
    
    def validate_model(self, model: str) -> bool:
        """
        Validate if a model is available.
        
        Args:
            model: Model name to validate
            
        Returns:
            True if model is available
        """
        available_models = self.get_available_models()
        return model in available_models
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """
        Get information about a specific model.
        
        Args:
            model: Model name
            
        Returns:
            Dictionary with model information
        """
        return {
            "provider": self.get_provider_type().value,
            "model": model,
            "available": self.validate_model(model),
            "cost_per_1k_tokens": self.cost_per_1k_tokens,
        }
    
    async def health_check(self) -> bool:
        """
        Perform a health check on the provider.
        
        Returns:
            True if provider is healthy
        """
        try:
            # Simple health check with minimal prompt
            response = await self.generate("Hello", max_tokens=5)
            return "text" in response
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False 