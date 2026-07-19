import redis
from functools import wraps
from flask import current_app
import json
import logging

logger = logging.getLogger(__name__)

class RedisCache:
    def __init__(self, redis_url):
        self.redis = redis.from_url(redis_url)
        self.ttl = current_app.config.get('CACHE_TTL', 300)

    def set(self, key, value, ttl=None):
        ttl = ttl or self.ttl
        self.redis.setex(key, ttl, json.dumps(value))

    def get(self, key):
        data = self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    def delete(self, key):
        self.redis.delete(key)

    def delete_pattern(self, pattern):
        for key in self.redis.scan_iter(pattern):
            self.redis.delete(key)

cache = None

def cache_with_ttl(ttl_seconds=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}".replace(' ', '_')
            cached = cache.get(key)
            if cached is not None:
                return cached

            result = func(*args, **kwargs)
            cache.set(key, result, ttl=ttl_seconds)
            return result
        return wrapper
    return decorator
