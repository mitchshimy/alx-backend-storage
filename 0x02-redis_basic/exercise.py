#!/usr/bin/env python3
"""
This module defines a Cache class that interfaces with a Redis database
to store and retrieve arbitrary data using randomly generated keys.
"""

import redis
import uuid
from typing import Union


class Cache:
    """
    Cache class to interact with a Redis database.
    It allows storing of data using generated keys.
    """

    def __init__(self) -> None:
        """
        Initialize the Redis client and flush the current database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Generate a random key, store the given data in Redis, and return the key.

        Args:
            data (Union[str, bytes, int, float]): The data to store.

        Returns:
            str: The key under which the data was stored.
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
