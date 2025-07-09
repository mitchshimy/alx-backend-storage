#!/usr/bin/env python3
"""
This module defines a Cache class that interfaces with a Redis database
to store and retrieve arbitrary data, track method call counts,
and log input/output history for decorated methods.
"""

import redis
import uuid
import functools
from typing import Union, Callable, Optional


def count_calls(method: Callable) -> Callable:
    """
    Decorator that counts how many times a method is called.
    Uses Redis to persist the count, keyed by the method's qualified name.
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__
        self._redis.incr(key)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    Decorator that stores the history of inputs and outputs for a function.
    Saves to Redis lists using keys <method_name>:inputs and <method_name>:outputs
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        input_key = method.__qualname__ + ":inputs"
        output_key = method.__qualname__ + ":outputs"

        self._redis.rpush(input_key, str(args))
        result = method(self, *args, **kwargs)
        self._redis.rpush(output_key, result)
        return result

    return wrapper


class Cache:
    """
    Cache class to interact with a Redis database.
    Supports storing, retrieving, counting calls, and logging I/O history.
    """

    def __init__(self) -> None:
        """
        Initialize the Redis client and flush the current database.
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @call_history
    @count_calls
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

    def get(self, key: str, fn: Optional[Callable] = None) -> Union[bytes, str, int, float, None]:
        """
        Retrieve the value from Redis using the given key and convert it using fn.

        Args:
            key (str): The Redis key.
            fn (Callable, optional): A function to convert the result.

        Returns:
            Union[bytes, str, int, float, None]: The value retrieved and possibly converted.
        """
        value = self._redis.get(key)
        if value is None:
            return None
        if fn:
            return fn(value)
        return value

    def get_str(self, key: str) -> Optional[str]:
        """
        Retrieve the value from Redis and decode it from bytes to UTF-8 string.

        Args:
            key (str): The Redis key.

        Returns:
            Optional[str]: The decoded string, or None if the key doesn't exist.
        """
        return self.get(key, fn=lambda d: d.decode("utf-8"))

    def get_int(self, key: str) -> Optional[int]:
        """
        Retrieve the value from Redis and convert it to an integer.

        Args:
            key (str): The Redis key.

        Returns:
            Optional[int]: The integer value, or None if the key doesn't exist.
        """
        return self.get(key, fn=int)
