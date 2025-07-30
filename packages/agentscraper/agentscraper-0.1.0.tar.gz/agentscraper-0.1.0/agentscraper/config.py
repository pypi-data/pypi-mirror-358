"""Configuration module for AgentScraper."""

from typing import Optional, Dict, Any
import os

class Config:
    """Configuration class for AgentScraper."""
    
    def __init__(self, llm_provider: str = "groq", llm_api_key: Optional[str] = None):
        """
        Initialize the configuration.
        
        Args:
            llm_provider (str): The LLM provider to use. Default is "groq".
            llm_api_key (str, optional): The API key for the LLM provider.
                If not provided, will try to get from environment variables.
        """
        self.llm_provider = llm_provider.lower()
        
        # Set API key
        self.llm_api_key = llm_api_key
        if not self.llm_api_key:
            env_var_name = f"{self.llm_provider.upper()}_API_KEY"
            self.llm_api_key = os.environ.get(env_var_name)
            
        if not self.llm_api_key:
            raise ValueError(f"No API key provided for {self.llm_provider}. "
                           f"Please provide it or set {env_var_name} environment variable.")
                           
        # Default settings
        self.user_agent = "AgentScraper/0.1.0"
        self.timeout = 30  # seconds
        self.max_retries = 3
        
    def get_provider_settings(self) -> Dict[str, Any]:
        """Get settings specific to the current LLM provider."""
        settings = {
            "api_key": self.llm_api_key,
        }
        
        if self.llm_provider == "groq":
            settings["model"] = "llama3-70b-8192"
        
        return settings