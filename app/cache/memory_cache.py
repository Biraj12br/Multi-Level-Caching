from cachetools import TTLCache

memory_cache = TTLCache(
    maxsize=1000,
    ttl=30
)