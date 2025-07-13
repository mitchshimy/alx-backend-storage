#!/usr/bin/env python3
"""
Expiring web cache and tracker using Redis
"""

import requests
import redis
from functools import wraps
from typing import Callable


def wrapper(method: Callable) -> Callable:
    """
    Decorator to track URL accesses and cache results
    """
    @wraps(method)
    def wrapped(url: str) -> str:
        """
        Wrapper function that handles caching and counting
        """
        # Initialize Redis connection inside wrapper
        redis_client = redis.Redis()
        
        # Track URL access count
        count_key = f"count:{url}"
        redis_client.incr(count_key)
        
        # Check cache first
        cache_key = f"result:{url}"
        cached_content = redis_client.get(cache_key)
        if cached_content:
            return cached_content.decode('utf-8')
        
        # Get fresh content if not in cache
        html_content = method(url)
        
        # Cache with 10 second expiration
        redis_client.setex(cache_key, 10, html_content)
        
        return html_content
    return wrapped


@wrapper
def get_page(url: str) -> str:
    """
    Get the HTML content of a URL with caching and access tracking
    
    Args:
        url: The URL to fetch content from
        
    Returns:
        The HTML content as a string
    """
    response = requests.get(url)
    return response.text
