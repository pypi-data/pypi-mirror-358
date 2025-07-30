"""Utility functions for AgentScraper."""

import json
from typing import Dict, Any, List, Union, Optional
import logging
import re
import time
import random

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('agentscraper')

def safe_json_loads(json_str: str, default: Any = None) -> Any:
    """
    Safely parse a JSON string.
    
    Args:
        json_str (str): JSON string to parse
        default (Any): Default value to return if parsing fails
        
    Returns:
        Any: Parsed JSON data or default value
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError) as e:
        # Try to extract JSON from text if it contains other content
        try:
            # Find content between square brackets which might be a JSON array
            import re
            match = re.search(r'\[(.*?)\]', json_str, re.DOTALL)
            if match:
                json_array = f"[{match.group(1)}]"
                return json.loads(json_array)
        except:
            pass
            
        logger.warning(f"Failed to parse JSON: {e}")
        return default

def extract_json_from_llm_response(response: str) -> Optional[Dict[str, Any]]:
    """
    Extract JSON data from LLM response that might contain additional text.
    
    Args:
        response (str): LLM response text
        
    Returns:
        Optional[Dict[str, Any]]: Extracted JSON data or None if extraction fails
    """
    # Find patterns that look like JSON objects
    json_pattern = r'\{(?:[^{}]|(?R))*\}'
    matches = re.findall(json_pattern, response)
    
    if not matches:
        return None
        
    # Try each match until we find valid JSON
    for match in matches:
        try:
            data = json.loads(match)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue
            
    return None

def exponential_backoff(
    func, max_retries: int = 5, initial_delay: float = 1.0, 
    max_delay: float = 60.0, factor: float = 2.0
):
    """
    Decorator to apply exponential backoff to a function.
    
    Args:
        func: Function to wrap
        max_retries (int): Maximum number of retry attempts
        initial_delay (float): Initial delay in seconds
        max_delay (float): Maximum delay in seconds
        factor (float): Factor by which to increase the delay
        
    Returns:
        Wrapped function with retry logic
    """
    def wrapper(*args, **kwargs):
        delay = initial_delay
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {e}")
                
                if attempt < max_retries - 1:
                    sleep_time = min(delay + random.uniform(0, 1), max_delay)
                    logger.info(f"Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                    delay *= factor
        
        logger.error(f"Function {func.__name__} failed after {max_retries} attempts")
        raise last_exception
        
    return wrapper