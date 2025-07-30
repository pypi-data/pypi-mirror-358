"""Query extraction agent that handles natural language instructions."""

from typing import Dict, Any, List
import json
import re
from bs4 import BeautifulSoup
from .BaseAgent import BaseAgent

class QueryAgent(BaseAgent):
    """Agent for extracting data based on natural language queries."""
    
    def __init__(self, llm_provider, agent_name="Query Extraction Agent"):
        """Initialize the query agent."""
        super().__init__(llm_provider, agent_name)
        
    def get_role(self) -> str:
        return "Data Extraction Specialist"
        
    def get_goal(self) -> str:
        return "extract specific data from web content based on natural language instructions"
        
    def get_backstory(self) -> str:
        return """I am an expert at interpreting natural language queries and extracting
        precisely the data requested from web content. I understand the structure of common
        websites and can identify patterns to extract names, counts, statistics, and other
        information."""
    
    def create_prompt(self, content: str, query: str) -> str:
        """
        Create a prompt for the LLM based on the user's query.
        
        Args:
            content (str): Content to process
            query (str): User's natural language query
            
        Returns:
            str: The formatted prompt
        """
        # Check if this is an e-commerce product extraction
        is_product_extraction = any(keyword in query.lower() for keyword in 
                                   ["product", "item", "price", "cost"])
        
        if is_product_extraction:
            prompt = f"""
            You are a {self.get_role()} specializing in e-commerce product data extraction.
            Your goal is to {self.get_goal()}.
            
            Background: {self.get_backstory()}
            
            QUERY: {query}
            
            IMPORTANT INSTRUCTIONS FOR PRODUCT EXTRACTION:
            1. ONLY extract actual products for sale, not navigation links, headers, or UI elements
            2. For prices, look for currency symbols (£, $, €) or patterns like "99.99" or "1,299"
            3. Make sure product names are complete and meaningful (not just fragments)
            4. Ignore elements like "Contact Us", "Track Order", login forms, etc.
            5. Look for sections of the page that contain product listings or product details
            
            Extract the exact data requested in the query from the HTML content below.
            Return your results as a structured JSON with these fields:
            - "items": An array of objects containing the extracted products
            - "count": The total number of products found
            
            Each product object should include:
            - "name": The product name
            - "price": The product price (as string with currency symbol if available)
            - "url": The product URL if available
            
            Return ONLY the JSON, with no additional text or explanation.
            
            HTML content to analyze:
            {content[:20000]}  # Allow more content for complex product pages
            """
        else:
            # Default prompt for non-product queries
            prompt = f"""
            You are a {self.get_role()}. 
            Your goal is to {self.get_goal()}.
            
            Background: {self.get_backstory()}
            
            QUERY: {query}
            
            Extract the exact data requested in the query from the HTML content below.
            Return your results as a structured JSON with these fields:
            - "items": An array of objects containing the extracted data
            - "count": The total number of items found
            
            Return ONLY the JSON, with no additional text or explanation.
            
            HTML content to analyze:
            {content[:15000]}
            """
        
        return prompt
    
    def _extract_products_fallback(self, content: str) -> Dict[str, Any]:
        """Fallback extraction using BeautifulSoup when LLM fails."""
        try:
            soup = BeautifulSoup(content, 'lxml')
            products = []
            
            # Try to find product items - common patterns in e-commerce sites
            # Look for product cards/containers
            product_elements = soup.select('.product, .product-item, .product-card, [data-product-id], .item')
            
            if not product_elements:
                # Try alternative selectors
                product_elements = soup.select('[itemtype*="Product"], .grid-item, .collection-item')
            
            for element in product_elements[:20]:  # Limit to 20 products
                name = None
                price = None
                url = None
                
                # Try to find name
                name_elem = element.select_one('.product-title, .product-name, h3, h2')
                if name_elem:
                    name = name_elem.get_text(strip=True)
                
                # Try to find price
                price_elem = element.select_one('.price, .product-price, [data-price]')
                if price_elem:
                    price = price_elem.get_text(strip=True)
                    
                # Try to find URL
                url_elem = element.select_one('a[href]')
                if url_elem and url_elem.get('href'):
                    url = url_elem['href']
                
                # Only add if we found at least a name
                if name and len(name) > 3:
                    products.append({
                        "name": name,
                        "price": price,
                        "url": url
                    })
            
            return {
                "items": products,
                "count": len(products)
            }
            
        except Exception as e:
            print(f"Fallback extraction error: {e}")
            return {
                "items": [],
                "count": 0,
                "error": str(e)
            }
    
    def process(self, content: str, query: str) -> Dict[str, Any]:
        """
        Process the content based on the user's query.
        
        Args:
            content (str): The HTML content to process.
            query (str): The natural language query.
            
        Returns:
            Dict[str, Any]: The extracted data.
        """
        try:
            # Pre-check if this is a product extraction query
            is_product_query = any(keyword in query.lower() for keyword in 
                                  ["product", "item", "price", "cost", "sale"])
                
            # Create the prompt for the LLM
            prompt = self.create_prompt(content, query)
            
            # Get completion from LLM
            response = self.llm_provider.get_completion(prompt)
            
            # Parse the JSON response
            try:
                result = json.loads(response)
                
                # Validation for product extraction
                if is_product_query:
                    # Filter out navigation items
                    if "items" in result and isinstance(result["items"], list):
                        # Remove items that are likely navigation elements
                        navigation_keywords = ["login", "cart", "account", "track", "order", "contact", 
                                            "about", "search", "home", "my account"]
                        
                        filtered_items = []
                        for item in result["items"]:
                            if isinstance(item, dict) and "name" in item:
                                # Skip items with names matching navigation elements
                                is_navigation = any(keyword in item["name"].lower() for keyword in navigation_keywords)
                                if not is_navigation and len(item["name"]) > 3:
                                    filtered_items.append(item)
                                    
                        result["items"] = filtered_items
                        result["count"] = len(filtered_items)
                
                return result
                
            except json.JSONDecodeError:
                # Try to extract JSON from text if it contains other content
                match = re.search(r'({.*})', response, re.DOTALL)
                if match:
                    try:
                        result = json.loads(match.group(1))
                        return result
                    except:
                        pass
            
            # If we can't parse the JSON and it's a product query, try fallback
            if is_product_query:
                print("LLM extraction failed, trying fallback extraction...")
                return self._extract_products_fallback(content)
            
            # Default fallback response
            return {
                "items": [],
                "count": 0,
                "error": "Failed to extract data"
            }
            
        except Exception as e:
            print(f"Error processing query: {e}")
            # Try fallback for product extraction
            if any(keyword in query.lower() for keyword in ["product", "item", "price"]):
                return self._extract_products_fallback(content)
                
            return {
                "items": [],
                "count": 0,
                "error": str(e)
            }