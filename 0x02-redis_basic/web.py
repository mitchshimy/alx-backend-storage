#!/usr/bin/env python3
"""
Module for caching HTML page content using Redis and tracking
access count for each URL with an expiration policy.
"""

import requests
import redis
from functools import wraps
from typing import Callable


# Create Redis client
r = redis.Redis()


def count_and_cache(fn: Callable[[str], str]) -> Callable[[str], str]:
    """
    Decorator that increments the access count for a URL and
    caches the HTML content for 10 seconds.
    """
    @wraps(fn)
    def wrapper(url: str) -> str:
        cache_key: str = f"cached:{url}"
        count_key: str = f"count:{url}"

        # Increment number of times the URL is accessed
        r.incr(count_key)

        # Try to get cached response
        cached: bytes = r.get(cache_key)
        if cached:
            return cached.decode("utf-8")

        # Not cached: make request and cache it
        result: str = fn(url)
        r.setex(cache_key, 10, result)
        return result

    return wrapper


@count_and_cache
def get_page(url: str) -> str:
    """
    Fetches the HTML content of a given URL and caches it
    using Redis for 10 seconds, while tracking access count.
    """
    response = requests.get(url)
    return response.text
