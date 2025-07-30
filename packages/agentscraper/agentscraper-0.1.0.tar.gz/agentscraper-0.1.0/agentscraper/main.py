"""Command-line interface for AgentScraper."""

import argparse
import json
import sys
import os
from typing import Dict, Any, Optional, Tuple
from . import AgentScraper

def check_selenium_installed():
    """Check if Selenium is installed."""
    try:
        import selenium
        import webdriver_manager
        return True
    except ImportError:
        return False

def find_browsers() -> Tuple[Optional[str], Optional[str]]:
    """
    Try to find Chrome and Edge binaries in common locations.
    
    Returns:
        Tuple[Optional[str], Optional[str]]: Paths to Chrome and Edge executables
    """
    # Possible Chrome paths
    chrome_paths = [
        # Windows paths
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Google\Chrome\Application\chrome.exe"),
        # Linux paths
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        # Mac paths
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    ]
    
    # Possible Edge paths
    edge_paths = [
        # Windows paths
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        os.path.join(os.environ.get('LOCALAPPDATA', ''), r"Microsoft\Edge\Application\msedge.exe"),
        # Linux paths
        "/usr/bin/microsoft-edge",
        "/usr/bin/microsoft-edge-stable",
        # Mac paths
        "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break
            
    edge_path = None
    for path in edge_paths:
        if os.path.exists(path):
            edge_path = path
            break
            
    return chrome_path, edge_path

def main():
    """Run the AgentScraper CLI."""
    parser = argparse.ArgumentParser(description="Extract data from Google search results using AI agents")
    
    # Add arguments
    parser.add_argument("query", help="Search query to process")
    parser.add_argument("--extract", choices=["all", "titles", "descriptions", "links", "prices", "faqs", "paragraphs", "lists", "tables"], 
                        default="titles", help="Type of content to extract")
    parser.add_argument("--results", type=int, default=10, help="Number of search results to process")
    parser.add_argument("--provider", choices=["groq", "openai", "claude", "gemini"], 
                        default="groq", help="LLM provider to use")
    parser.add_argument("--api-key", help="API key for the LLM provider")
    parser.add_argument("--output", help="Output file path (JSON format)")
    parser.add_argument("--no-selenium", action="store_true", help="Disable Selenium and use requests only")
    parser.add_argument("--chrome-path", help="Path to Chrome binary")
    parser.add_argument("--edge-path", help="Path to Edge binary")
    
    args = parser.parse_args()
    
    # Check selenium if needed
    use_selenium = not args.no_selenium
    if use_selenium and not check_selenium_installed():
        print("Warning: Selenium is not installed. For better results, run: pip install selenium webdriver-manager")
        print("Falling back to requests-based scraping...")
        use_selenium = False
        
    # Find browser binaries if not specified
    chrome_path = args.chrome_path
    edge_path = args.edge_path
    
    if use_selenium and (not chrome_path or not edge_path):
        auto_chrome_path, auto_edge_path = find_browsers()
        
        if not chrome_path and auto_chrome_path:
            chrome_path = auto_chrome_path
            print(f"Found Chrome at: {chrome_path}")
            
        if not edge_path and auto_edge_path:
            edge_path = auto_edge_path
            print(f"Found Edge at: {edge_path}")
            
        if not chrome_path and not edge_path:
            print("Warning: Neither Chrome nor Edge was found. You may need to specify a path with --chrome-path or --edge-path")
    
    try:
        # Initialize AgentScraper
        scraper = AgentScraper(llm_provider=args.provider, llm_api_key=args.api_key, 
                               use_selenium=use_selenium, chrome_path=chrome_path, edge_path=edge_path)
        
        # Extract data based on the specified type
        result = None
        if args.extract == "titles":
            result = scraper.extract_titles(args.query, args.results)
        else:
            result = scraper.extract_content(args.query, args.extract, args.results)
        
        # Output results
        output_json = json.dumps(result, indent=2)
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output_json)
            print(f"Results saved to {args.output}")
        else:
            print(output_json)
            
        return 0
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())