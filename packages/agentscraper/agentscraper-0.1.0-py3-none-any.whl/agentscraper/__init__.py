"""
AgentScraper: Agent-based web scraping with LLM integration.
"""

from typing import Dict, Any, Optional, List, Set
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
from .config import Config
from .llm.groq import GroqProvider
from .agent.TitleAgent import TitleAgent
from .agent.QueryAgent import QueryAgent

__version__ = "0.1.0"

class AgentScraper:
    """Main AgentScraper class."""
    
    def __init__(self, llm_provider: str = "groq", llm_api_key: Optional[str] = None, 
                 chrome_path: Optional[str] = None, edge_path: Optional[str] = None):
        """
        Initialize AgentScraper.
        
        Args:
            llm_provider (str): LLM provider to use. Currently only "groq" is supported.
            llm_api_key (str, optional): API key for the LLM provider.
            chrome_path (str, optional): Path to Chrome binary.
            edge_path (str, optional): Path to Edge binary.
        """
        self.config = Config(llm_provider=llm_provider, llm_api_key=llm_api_key)
        
        # Initialize LLM provider
        provider_settings = self.config.get_provider_settings()
        if llm_provider == "groq":
            self.llm = GroqProvider(**provider_settings)
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_provider}")
            
        # Initialize headers for requests
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
        }
        
        self.timeout = self.config.timeout
        self.chrome_path = chrome_path
        self.edge_path = edge_path
    
    def _get_base_url(self, url: str) -> str:
        """Extract the base URL from a full URL."""
        parsed = urllib.parse.urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"
    
    def _is_same_domain(self, url: str, base_domain: str) -> bool:
        """Check if a URL belongs to the same domain as the base URL."""
        if not url.startswith('http'):
            return True  # Relative URL
        return urllib.parse.urlparse(url).netloc == urllib.parse.urlparse(base_domain).netloc
    
    def _normalize_url(self, url: str, base_url: str) -> str:
        """Convert relative URLs to absolute URLs."""
        if not url.startswith('http'):
            return urllib.parse.urljoin(base_url, url)
        return url
    
    def scrape_website(self, start_url: str, max_pages: int = 50, crawl_delay: float = 1.0) -> Dict[str, Any]:
        """
        Scrape a website starting from a URL and extract content from all its pages.
        
        Args:
            start_url (str): Starting URL to begin scraping from.
            max_pages (int): Maximum number of pages to scrape.
            crawl_delay (float): Delay between requests in seconds.
            
        Returns:
            Dict[str, Any]: Dictionary containing all scraped pages and their content.
        """
        base_url = self._get_base_url(start_url)
        base_domain = urllib.parse.urlparse(base_url).netloc
        
        # Track pages to visit and visited pages
        to_visit = {start_url}
        visited = set()
        scraped_content = {}
        
        print(f"Starting website scrape at: {start_url}")
        print(f"Base domain: {base_domain}")
        
        # Breadth-first crawling
        while to_visit and len(visited) < max_pages:
            # Get next URL to visit
            current_url = to_visit.pop()
            if current_url in visited:
                continue
                
            # Add to visited set
            visited.add(current_url)
            
            print(f"Scraping page {len(visited)}/{max_pages}: {current_url}")
            
            try:
                # Fetch page content
                response = requests.get(current_url, headers=self.headers, timeout=self.timeout)
                
                # Skip non-HTML content
                content_type = response.headers.get('Content-Type', '')
                if 'text/html' not in content_type.lower():
                    print(f"Skipping non-HTML content: {content_type}")
                    continue
                    
                # Parse with BeautifulSoup
                soup = BeautifulSoup(response.text, 'lxml')
                
                # Store raw parsed content
                scraped_content[current_url] = {
                    'html': response.text,
                    'soup': soup,
                    'title': soup.title.text if soup.title else '',
                    'text': soup.get_text(separator=' ', strip=True)
                }
                
                # Find links to other pages on the same domain
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    
                    # Skip anchors, javascript, and mailto links
                    if href.startswith('#') or href.startswith('javascript:') or href.startswith('mailto:'):
                        continue
                        
                    # Normalize URL
                    full_url = self._normalize_url(href, base_url)
                    
                    # Only add URLs from the same domain
                    if self._is_same_domain(full_url, base_url) and full_url not in visited:
                        to_visit.add(full_url)
                
                # Wait between requests
                time.sleep(crawl_delay)
                
            except Exception as e:
                print(f"Error scraping {current_url}: {e}")
        
        print(f"Scraping completed. Visited {len(visited)} pages.")
        return {
            'base_url': base_url,
            'pages_visited': len(visited),
            'urls_visited': list(visited),
            'content': scraped_content
        }
    
    def extract_data(self, website_data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """
        Extract specific data from scraped website content.
        
        Args:
            website_data (Dict[str, Any]): Data returned from scrape_website method.
            data_type (str): Type of data to extract (titles, headings, links, etc.)
                            or a natural language query.
                
        Returns:
            Dict[str, Any]: Dictionary containing extracted data.
        """
        print(f"Extracting data based on: {data_type}")
        
        # Check if data_type is a predefined type or a natural language query
        predefined_types = ["titles", "headings", "links", "paragraphs"]
        
        if data_type in predefined_types:
            # Original implementation for predefined types
            results = {}
            
            # First use bs4 to extract raw data from each page
            for url, page_data in website_data['content'].items():
                soup = page_data['soup']
                
                # Extract different types of data based on data_type
                if data_type == "titles":
                    # Extract page titles
                    page_title = page_data['title']
                    results[url] = {
                        'raw': page_title,
                        'processed': None  # Will be filled by agent processing
                    }
                
                elif data_type == "headings":
                    # Extract all headings
                    headings = []
                    for tag in soup.find_all(['h1', 'h2', 'h3']):
                        text = tag.get_text(strip=True)
                        if text:
                            headings.append({
                                'level': tag.name,
                                'text': text
                            })
                    results[url] = {
                        'raw': headings,
                        'processed': None  # Will be filled by agent processing
                    }
                
                elif data_type == "links":
                    # Extract all links
                    links = []
                    for link in soup.find_all('a', href=True):
                        href = link['href']
                        text = link.get_text(strip=True)
                        if href and not href.startswith('#'):
                            links.append({
                                'href': href,
                                'text': text
                            })
                    results[url] = {
                        'raw': links,
                        'processed': None  # Will be filled by agent processing
                    }
                
                elif data_type == "paragraphs":
                    # Extract paragraphs
                    paragraphs = []
                    for p in soup.find_all('p'):
                        text = p.get_text(strip=True)
                        if text and len(text) > 20:  # Filter out very short paragraphs
                            paragraphs.append(text)
                    results[url] = {
                        'raw': paragraphs,
                        'processed': None  # Will be filled by agent processing
                    }
                
                else:
                    # Default extraction - just get all text content
                    results[url] = {
                        'raw': page_data['text'],
                        'processed': None  # Will be filled by agent processing
                    }
            
            # Process with specific agents
            if data_type == "titles":
                agent = TitleAgent(self.llm)
                
                for url, data in results.items():
                    # Process with the agent
                    if data['raw']:
                        agent_results = agent.process(f"<title>{data['raw']}</title>")
                        if agent_results["titles"]:
                            data['processed'] = agent_results["titles"][0]
                        else:
                            data['processed'] = data['raw']
            
            return {
                'data_type': data_type,
                'page_count': len(results),
                'results': results
            }
        else:
            # Handle natural language query using QueryAgent
            query_agent = QueryAgent(self.llm)
            combined_results = {
                'data_type': 'custom_query',
                'query': data_type,
                'items': []
            }
            
            # Process each page with the query agent
            for url, page_data in website_data['content'].items():
                # Use the full HTML content
                agent_results = query_agent.process(page_data['html'], data_type)
                
                # Store the URL with each result item for context
                if 'items' in agent_results and isinstance(agent_results['items'], list):
                    for item in agent_results['items']:
                        if isinstance(item, dict):
                            item['source_url'] = url
                    
                    # Add these items to our combined results
                    combined_results['items'].extend(agent_results['items'])
            
            # Update the total count
            combined_results['count'] = len(combined_results['items'])
            
            return combined_results
    
    def scrape_and_extract(self, url: str, data_type: str, max_pages: int = 50) -> Dict[str, Any]:
        """
        Scrape a website and extract specific data.
        
        Args:
            url (str): URL to start scraping from.
            data_type (str): Type of data to extract.
            max_pages (int): Maximum number of pages to scrape.
            
        Returns:
            Dict[str, Any]: Dictionary containing extraction results.
        """
        # First scrape the website
        website_data = self.scrape_website(url, max_pages)
        
        # Then extract the requested data
        return self.extract_data(website_data, data_type)