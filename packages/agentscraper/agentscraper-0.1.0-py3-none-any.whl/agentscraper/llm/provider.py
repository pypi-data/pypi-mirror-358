"""Base LLM provider module."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class LLMProvider(ABC):
    """Base class for LLM providers."""
    
    def __init__(self, api_key: str, **kwargs):
        """
        Initialize the LLM provider.
        
        Args:
            api_key (str): The API key for the provider.
            **kwargs: Additional provider-specific settings.
        """
        self.api_key = api_key
        self.kwargs = kwargs
        self._client = None
    
    @property
    @abstractmethod
    def client(self):
        """Get the client for the LLM provider."""
        pass
        
    @abstractmethod
    def get_completion(self, prompt: str, **kwargs) -> str:
        """
        Get a completion from the LLM provider.
        
        Args:
            prompt (str): The prompt to send to the LLM.
            **kwargs: Additional parameters for the completion.
            
        Returns:
            str: The completion text.
        """
        pass