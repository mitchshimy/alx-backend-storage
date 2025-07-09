#!/usr/bin/env python3
"""
This module provides a function to fetch web pages with caching and tracking.
Each URL's access count is tracked and its content is cached for 10 seconds.
"""

import requests
import redis
from typing import Callable
from functools import wraps

# Create a Redis client
redis_client = redis.Redis()


def cache_page(func: Callable) -> Callable:
    """
    Decorator that caches the result of a web page fetch for 10 seconds
    and tracks the number of times each URL was accessed.
    """

    @wraps(func)
    def wrapper(url: str) -> str:
        count_key = f"count:{url}"
        redis_client.incr(count_key)

        cached_html = redis_client.get(url)
        if cached_html:
            return cached_html.decode("utf-8")

        html = func(url)
        redis_client.setex(url, 10, html)
        return html

    return wrapper


@cache_page
def get_page(url: str) -> str:
    """
    Fetch the HTML content of the specified URL.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The HTML content of the page.
    """
    response = requests.get(url)
    return response.text
