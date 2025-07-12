#!/usr/bin/env python3
"""
Redis basic operations module
"""
import redis
import uuid
from typing import Union, Callable, Optional
from functools import wraps


def count_calls(method: Callable) -> Callable:
    """Decorator to count method calls"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function that increments call count"""
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store history of inputs and outputs"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Wrapper function that stores input/output history"""
        input_key = f"{method.__qualname__}:inputs"
        output_key = f"{method.__qualname__}:outputs"
        
        # Store input
        self._redis.rpush(input_key, str(args))
        
        # Execute method and store output
        output = method(self, *args, **kwargs)
        self._redis.rpush(output_key, str(output))
        
        return output
    return wrapper


def replay(method: Callable) -> None:
    """Display the history of calls of a particular function"""
    # Access Redis instance from the Cache class, assuming method is Cache.store
    redis_instance = method.__self__._redis  # Use the Redis instance from the Cache class
    input_key = f"{method.__qualname__}:inputs"
    output_key = f"{method.__qualname__}:outputs"
    
    inputs = redis_instance.lrange(input_key, 0, -1)
    outputs = redis_instance.lrange(output_key, 0, -1)
    
    call_count = len(inputs)
    if call_count == 0:
        print(f"{method.__qualname__} was called 0 times:")
        return
    
    print(f"{method.__qualname__} was called {call_count} times:")
    for inp, out in zip(inputs, outputs):
        input_str = inp.decode("utf-8")
        print(f"{method.__qualname__}(*{input_str}) -> {out.decode('utf-8')}")


class Cache:
    """Cache class using Redis"""
    
    def __init__(self):
        """Initialize Redis client and flush database"""
        self._redis = redis.Redis()
        self._redis.flushdb()
    
    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis with random key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
    
    def get(self, key: str, fn: Optional[Callable] = None) -> Union[str, bytes, int, float, None]:
        """Get data from Redis with optional conversion"""
        data = self._redis.get(key)
        if data is None:
            return None
        if fn is not None:
            return fn(data)
        return data
    
    def get_str(self, key: str) -> Optional[str]:
        """Get string from Redis"""
        return self.get(key, lambda d: d.decode("utf-8"))
    
    def get_int(self, key: str) -> Optional[int]:
        """Get integer from Redis"""
        return self.get(key, int)
