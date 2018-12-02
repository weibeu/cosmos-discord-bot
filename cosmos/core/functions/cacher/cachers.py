import cachetools

from abc import ABC, abstractmethod


class Cache(object):

    @abstractmethod
    def get(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def pop(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def keys(self, *args, **kwargs):
        raise NotImplementedError

    def get_cache(self, key: str or int):
        return self.get(key)

    def set_cache(self, key: str or int, value):
        self.update({key: value})

    def remove_cache(self, key: str or int):
        if key in self.keys():
            self.pop(key)


class DictCache(dict, Cache):

    def __init__(self):
        super().__init__()

    def get(self, key: str or int):
        return super().get(key)


class TTLCache(Cache):

    def __init__(self, max_size: int=50000, ttl: int=60, **kwargs):
        super().__init__(cachetools.TTLCache(max_size, ttl, **kwargs))


class LRUCache(Cache):

    def __init__(self, max_size: int=50000, **kwargs):
        super().__init__(cachetools.LRUCache(max_size, **kwargs))


class LFUCache(Cache):

    def __init__(self, max_size: int=50000, **kwargs):
        super().__init__(cachetools.LFUCache(max_size, **kwargs))


class RedisCache(object):

    def __init__(self):
        pass
