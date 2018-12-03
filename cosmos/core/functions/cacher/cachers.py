import pickle
import aioredis
import cachetools

from abc import ABC, abstractmethod


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

    # TODO: Make child classes implement abstractmethod(s) from different parent class.


class DictCache(dict, Cache):

    def __init__(self):
        super().__init__()


class TTLCache(cachetools.TTLCache, Cache):

    def __init__(self, max_size: int=50000, ttl: int=60, **kwargs):
        super().__init__(max_size, ttl, **kwargs)


class LRUCache(cachetools.LRUCache, Cache):

    def __init__(self, max_size: int=50000, **kwargs):
        super().__init__(max_size, **kwargs)


class LFUCache(cachetools.LFUCache, Cache):

    def __init__(self, max_size: int=50000, **kwargs):
        super().__init__(max_size, **kwargs)


class AsyncDictCache(DictCache):

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


class RedisCache(object):

    def __init__(self):
        self.__client = None

    async def _fetch_client(self):
        # TODO: Start redis server.
        self.__client = await aioredis.create_redis('redis://localhost')

    async def get(self, key: str):
        byte = await self.__client.get(key)
        if byte:
            data = pickle.loads(byte)
        else:
            data = None
        return data

    async def set(self, key: str, data):
        byte = pickle.dumps(data)
        await self.__client.set(key, byte)

    async def remove(self, key: str):
        if await self.__client.exists(key):
            await self.__client.delete(key)
