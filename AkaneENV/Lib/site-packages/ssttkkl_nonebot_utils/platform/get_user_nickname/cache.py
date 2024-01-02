from cachetools import TTLCache

cache = TTLCache(1024, 3600)
