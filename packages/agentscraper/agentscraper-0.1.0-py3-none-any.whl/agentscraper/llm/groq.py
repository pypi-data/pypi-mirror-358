"""Groq LLM provider."""

import groq
from typing import Dict, Any, Optional
from .provider import LLMProvider

class GroqProvider(LLMProvider):
    """Groq LLM provider implementation."""
    
    def __init__(self, api_key: str, model: str = "llama3-70b-8192", **kwargs):
        """
        Initialize the Groq provider.
        
        Args:
            api_key (str): The Groq API key.
            model (str): The model to use. Default is "llama3-70b-8192".
            **kwargs: Additional settings.
        """
        super().__init__(api_key, **kwargs)
        self.model = model
        
    @property
    def client(self):
        """Get the Groq client."""
        if self._client is None:
            self._client = groq.Client(api_key=self.api_key)
        return self._client
    
    def get_completion(self, prompt: str, **kwargs) -> str:
        """
        Get a completion from Groq.
        
        Args:
            prompt (str): The prompt to send to Groq.
            **kwargs: Additional parameters for the completion.
            
        Returns:
            str: The completion text.
        """
        # Default parameters
        params = {
            "model": self.model,
            "max_tokens": 1000,
            "temperature": 0.7,
        }
        
        # Update with any provided parameters
        params.update(kwargs)
        
        # Make the completion request
        response = self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            **params
        )
        
        return response.choices[0].message.content