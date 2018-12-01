import cachetools


class Cache(object):

    def __init__(self, cache):
        self.cache = cache

    def get_cache(self, key: str or int):
        return self.cache.get(key)

    def set_cache(self, key: str or int, value):
        self.cache.update({key: value})

    def remove_cache(self, key: str or int):
        if key in self.cache.keys():
            self.cache.pop(key)


class DictCache(Cache):

    def __init__(self):
        super().__init__(dict())


class TTLCache(Cache):

    def __init__(self, max_size: int=50000, ttl: int=60, **kwargs):
        super().__init__(cachetools.TTLCache(max_size, ttl, **kwargs))


class LRUCache(Cache):

    def __init__(self, max_size: int=50000, **kwargs):
        super().__init__(cachetools.LRUCache(max_size, **kwargs))


class LFUCache(Cache):

    def __init__(self, max_size: int=50000, **kwargs):
        super().__init__(cachetools.LFUCache(max_size, **kwargs))
