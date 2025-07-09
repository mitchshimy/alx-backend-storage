#!/usr/bin/env python3
"""
Module that implements a web cache and tracker using Redis.
Caches page HTML for 10 seconds and tracks access count for each URL.
"""

import redis
import requests
from functools import wraps
from typing import Callable

# Redis connection
redis_client = redis.Redis()


def count_access(method: Callable) -> Callable:
    """
    Decorator that tracks how many times a URL has been accessed.
    Increments 'count:{url}' every time the function is called.
    """

    @wraps(method)
    def wrapper(url: str) -> str:
        redis_client.incr(f"count:{url}")
        cached = redis_client.get(url)

        if cached:
            return cached.decode('utf-8')

        result = method(url)
        redis_client.setex(url, 10, result)
        return result

    return wrapper


@count_access
def get_page(url: str) -> str:
    """
    Retrieve the HTML content of a URL, with caching and access tracking.

    Args:
        url (str): The URL to retrieve.

    Returns:
        str: The HTML content of the page.
    """
    response = requests.get(url)
    return response.text
