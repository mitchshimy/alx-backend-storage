#!/usr/bin/env python3
"""
This module implements an expiring web cache and tracker using Redis.
It provides functionality to fetch web pages while tracking access counts
and caching responses with expiration to optimize repeated requests.
"""

import requests
import redis
from functools import wraps
from typing import Callable, Optional


def url_access_tracker(method: Callable) -> Callable:
    """
    Decorator function that tracks URL access counts and caches responses.
    
    Args:
        method (Callable): The function to be decorated (get_page in this case)
    
    Returns:
        Callable: The wrapped function with caching and tracking functionality
    """
    @wraps(method)
    def wrapper(url: str) -> str:
        """
        Wrapper function that handles the caching and access tracking logic.
        
        Args:
            url (str): The URL to fetch content from
            
        Returns:
            str: The HTML content of the requested URL
        """
        redis_client = redis.Redis()
        count_key = f"count:{url}"
        cache_key = f"cache:{url}"

        # Increment access count
        redis_client.incr(count_key)

        # Check for cached content
        cached_content: Optional[bytes] = redis_client.get(cache_key)
        if cached_content:
            return cached_content.decode('utf-8')

        # Fetch fresh content if not cached
        html_content: str = method(url)
        
        # Cache the content with 10 second expiration
        redis_client.setex(cache_key, 10, html_content)
        
        return html_content
    return wrapper


@url_access_tracker
def get_page(url: str) -> str:
    """
    Fetches the HTML content of a specified URL with caching and access tracking.
    
    Args:
        url (str): The URL to fetch content from
        
    Returns:
        str: The HTML content of the page
        
    Raises:
        requests.exceptions.RequestException: If the request fails
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text


if __name__ == "__main__":
    """Test the caching and tracking functionality."""
    test_url = "http://slowwly.robertomurray.co.uk/delay/1000/url/http://www.google.com"
    
    # First request (will be slow)
    print(get_page(test_url))
    
    # Second request (should be fast from cache)
    print(get_page(test_url))
    
    # Display access count
    redis_client = redis.Redis()
    count = redis_client.get(f"count:{test_url}")
    print(f"URL accessed {int(count) if count else 0} times")
