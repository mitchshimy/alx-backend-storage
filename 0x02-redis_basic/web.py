#!/usr/bin/env python3
"""
This module implements an expiring web cache and tracker using Redis.
"""

import requests
import redis
from functools import wraps
from typing import Callable

# Initialize Redis connection
redis_client = redis.Redis()


def track_and_cache(expiration: int = 10) -> Callable:
    """
    Decorator to track URL access counts and cache responses with expiration.

    Args:
        expiration (int): Cache expiration time in seconds (default: 10)
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(url: str) -> str:
            # Track URL access count
            count_key = f"count:{url}"
            redis_client.incr(count_key)

            # Check cache first
            cache_key = f"cache:{url}"
            cached_content = redis_client.get(cache_key)
            if cached_content:
                return cached_content.decode('utf-8')

            # Get fresh content if not in cache
            content = func(url)

            # Cache the content with expiration
            redis_client.setex(cache_key, expiration, content)
            return content
        return wrapper
    return decorator


@track_and_cache(expiration=10)
def get_page(url: str) -> str:
    """
    Get the HTML content of a URL with caching and access tracking.

    Args:
        url (str): The URL to fetch

    Returns:
        str: The HTML content of the page
    """
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    # Test with a slow URL
    slow_url = "http://slowwly.robertomurray.co.uk/delay/1000/url/http://www.google.com"
    print(get_page(slow_url))  # First call - slow
    print(get_page(slow_url))  # Second call - fast (cached)
    print(f"Access count: {redis_client.get(f'count:{slow_url}').decode('utf-8')}")
