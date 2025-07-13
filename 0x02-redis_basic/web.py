#!/usr/bin/env python3
"""
Web cache and tracker module
"""
import redis
import requests
from typing import Callable
from functools import wraps

# Initialize a single Redis client to ensure consistency
_redis = redis.Redis(decode_responses=False)  # Keep responses as bytes

def track_url_access(method: Callable) -> Callable:
    """Decorator to track URL access count and cache results"""
    @wraps(method)
    def wrapper(url: str) -> str:
        """Wrapper function for tracking and caching"""
        # Increment access count
        count_key = f"count:{url}"
        _redis.incr(count_key)
        
        # Check cache
        cache_key = f"cache:{url}"
        cached_content = _redis.get(cache_key)
        
        if cached_content:
            return cached_content.decode("utf-8")
        
        # Get content and cache it
        try:
            content = method(url)
            # Ensure content is stored as bytes
            _redis.setex(cache_key, 10, content.encode("utf-8"))
            return content
        except requests.RequestException:
            return ""  # Return empty string on failure
    
    return wrapper

@track_url_access
def get_page(url: str) -> str:
    """Get HTML content of a URL"""
    try:
        response = requests.get(url, timeout=5)  # Add timeout for reliability
        response.raise_for_status()  # Raise exception for bad status codes
        return response.text
    except requests.RequestException:
        return ""  # Handle errors gracefully
