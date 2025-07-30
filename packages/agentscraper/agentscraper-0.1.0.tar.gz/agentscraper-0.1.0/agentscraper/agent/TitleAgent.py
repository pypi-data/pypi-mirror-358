"""Title extraction agent."""

from typing import Dict, Any, List
import json
import re
from bs4 import BeautifulSoup
from .BaseAgent import BaseAgent

class TitleAgent(BaseAgent):
    """Agent for extracting titles from Google search results."""
    
    def __init__(self, llm_provider, agent_name="Title Extraction Agent"):
        """Initialize the title agent."""
        super().__init__(llm_provider, agent_name)
        
    def get_role(self) -> str:
        return "Title Extraction Specialist"
        
    def get_goal(self) -> str:
        return "extract all meaningful and relevant titles from web content with high accuracy"
        
    def get_backstory(self) -> str:
        return """I am an expert at identifying and extracting meaningful titles from web content.
        I can distinguish between actual content titles and UI elements or navigation.
        My specialty is finding the most relevant titles that represent the main content."""
    
    def _extract_titles_via_bs4(self, content: str) -> List[str]:
        """Use BeautifulSoup as fallback to extract titles from HTML."""
        try:
            soup = BeautifulSoup(content, 'lxml')
            titles = []
            
            # Extract h3 tags (Google search results typically use h3 for titles)
            for heading in soup.find_all('h3'):
                if heading.text.strip():
                    titles.append(heading.text.strip())
            
            # If no h3 tags found, try other common elements
            if not titles:
                # Look for Google result containers and extract their text
                for div in soup.select('div.g div.yuRUbf a'):
                    if div.text.strip():
                        titles.append(div.text.strip())
                
                # Try to find any other elements that might contain titles
                for elem in soup.find_all(['h1', 'h2', 'h3', 'h4', 'strong']):
                    if elem.text.strip() and len(elem.text.strip()) > 10:  # Minimum title length
                        titles.append(elem.text.strip())
            
            return titles
        except Exception as e:
            print(f"Error extracting titles with BeautifulSoup: {e}")
            return []
        
    def process(self, content: str) -> Dict[str, Any]:
        """
        Extract titles from the provided content.
        
        Args:
            content (str): The HTML content from Google search results.
            
        Returns:
            Dict[str, Any]: Dictionary with extracted titles and metadata.
        """
        # First try direct extraction with BeautifulSoup
        bs4_titles = self._extract_titles_via_bs4(content)
        
        # If we get good results from BeautifulSoup, use those
        if len(bs4_titles) >= 10:  # If we find at least 5 titles, consider it successful
            return {
                "titles": bs4_titles,
                "count": len(bs4_titles),
                "method": "bs4"
            }
        
        # Otherwise, try with LLM
        try:
            # Create the prompt for the LLM
            prompt = self.create_prompt(content)
            
            # Get completion from LLM
            response = self.llm_provider.get_completion(prompt)
            
            # Parse the results
            try:
                titles = json.loads(response)
                if not isinstance(titles, list):
                    titles = []
            except (json.JSONDecodeError, TypeError):
                # Try to extract JSON from text if it contains other content
                try:
                    match = re.search(r'\[(.*?)\]', response, re.DOTALL)
                    if match:
                        json_array = f"[{match.group(1)}]"
                        titles = json.loads(json_array)
                    else:
                        titles = bs4_titles  # Fall back to BS4 results
                except:
                    titles = bs4_titles  # Fall back to BS4 results
        except Exception:
            titles = bs4_titles  # Fall back to BS4 results
            
        # If LLM extraction failed, use BS4 results (which might be empty)
        if not titles:
            titles = bs4_titles
            
        # Deduplicate and clean the titles
        clean_titles = []
        for title in titles:
            if isinstance(title, str) and title.strip() and title.strip() not in clean_titles:
                clean_titles.append(title.strip())
            
        return {
            "titles": clean_titles,
            "count": len(clean_titles),
            "method": "llm" if titles != bs4_titles else "bs4"
        }