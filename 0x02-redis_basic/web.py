#!/usr/bin/env python3
"""
Expiring web cache tracker using Redis
"""

import requests
import redis
from functools import wraps
from typing import Callable

# Initialize Redis connection
r = redis.Redis()


def count_and_cache(fn: Callable) -> Callable:
    """
    Decorator to count accesses and cache results for 10 seconds
    """
    @wraps(fn)
    def wrapper(url: str) -> str:
        cache_key = f"cached:{url}"
        count_key = f"count:{url}"

        # Increment count every time it's requested
        r.incr(count_key)

        # Check if cached response exists
        cached = r.get(cache_key)
        if cached:
            return cached.decode("utf-8")

        # If not cached, call the function
        result = fn(url)

        # Cache the result for 10 seconds
        r.setex(cache_key, 10, result)

        return result

    return wrapper


@count_and_cache
def get_page(url: str) -> str:
    """
    Fetches the page content from a URL, with Redis-based caching and counting
    """
    response = requests.get(url)
    return response.text
