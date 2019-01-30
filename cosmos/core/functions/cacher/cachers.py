import pickle
from abc import ABC, abstractmethod

import aioredis
import cachetools


class Cache(object):

    __metaclass__ = ABC

    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def pop(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def keys(self, *args, **kwargs):
        raise NotImplementedError

    @abstractmethod
    def get(self, key: str or int):
        raise NotImplementedError

    def set(self, key: str or int, data):
        self.update({key: data})

    def remove(self, key: str or int):
        if key in self.keys():
            self.pop(key)


class DictCache(dict, Cache, ABC):

    def __init__(self):
        super().__init__()


class TTLCache(cachetools.TTLCache, Cache, ABC):

    def __init__(self, max_size: int = 50000, ttl: int = 60, **kwargs):
        super().__init__(max_size, ttl, **kwargs)


class LRUCache(cachetools.LRUCache, Cache, ABC):

    def __init__(self, max_size: int = 50000, **kwargs):
        super().__init__(max_size, **kwargs)


class LFUCache(cachetools.LFUCache, Cache, ABC):

    def __init__(self, max_size: int = 50000, **kwargs):
        super().__init__(max_size, **kwargs)


class AsyncDictCache(DictCache, ABC):

    def __init__(self):
        super().__init__()

    async def get(self, key: str):
        byte = super().get(key)
        if byte:
            data = pickle.loads(byte)
        else:
            data = None
        return data

    async def set(self, key: str, data):
        byte = pickle.dumps(data)
        super().update({key: byte})

    async def remove(self, key: str):
        if key in super().keys():
            super().pop(key)


class RedisCache(aioredis.Redis, ABC):

    def __init__(self, connection):
        self._conn = connection
        super().__init__(self._conn)

    async def get(self, key: str, **kwargs):
        byte = await super().get(key)
        if byte:
            data = pickle.loads(byte)
        else:
            data = None
        return data

    async def set(self, key: str, data, **kwargs):
        byte = pickle.dumps(data)
        await super().set(key, byte)

    async def remove(self, key: str):
        if await self.exists(key):
            await self.delete(key)
