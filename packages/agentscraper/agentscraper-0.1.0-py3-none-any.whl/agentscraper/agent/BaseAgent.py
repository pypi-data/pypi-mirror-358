"""Base agent for AgentScraper."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List

class BaseAgent(ABC):
    """Base class for AgentScraper agents."""
    
    def __init__(self, llm_provider, agent_name: str):
        """
        Initialize the base agent.
        
        Args:
            llm_provider: The LLM provider to use.
            agent_name (str): Name of the agent.
        """
        self.llm_provider = llm_provider
        self.agent_name = agent_name
        
    @abstractmethod
    def get_role(self) -> str:
        """Get the agent's role description."""
        pass
        
    @abstractmethod
    def get_goal(self) -> str:
        """Get the agent's goal."""
        pass
        
    @abstractmethod
    def get_backstory(self) -> str:
        """Get the agent's backstory."""
        pass
        
    def create_prompt(self, content: str) -> str:
        """
        Create a prompt for the LLM based on the agent's role and task.
        
        Args:
            content (str): Content to process
            
        Returns:
            str: The formatted prompt
        """
        prompt = f"""
        You are a {self.get_role()}. 
        Your goal is to {self.get_goal()}.
        
        Background: {self.get_backstory()}
        
        Extract all meaningful titles from the HTML content below.
        Focus only on actual content titles and ignore navigation elements, ads, and other UI components.
        Return ONLY a JSON array of strings, with no explanation or additional text.
        
        Example response format:
        ["First Title", "Second Title", "Another Important Title"]
        
        HTML content to analyze:
        {content[:8000]}  # Truncate to avoid token limits
        """
        return prompt
    
    @abstractmethod
    def process(self, content: str) -> Dict[str, Any]:
        """
        Process the content with this agent.
        
        Args:
            content (str): The content to process.
            
        Returns:
            Dict[str, Any]: The extracted data.
        """
        pass