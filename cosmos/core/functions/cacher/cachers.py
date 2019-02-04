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
        # byte = super().get(key)
        # if byte:
        #    data = pickle.loads(byte)
        # else:
        #    data = None
        return super().get(key, dict())

    async def set(self, key: str, data):
        # byte = pickle.dumps(data)
        super().update({key: data})

    async def remove(self, key: str):
        if key in super().keys():
            super().pop(key)

    async def set_object(self, key: str, field, data):
        d = await self.get(key)
        d[field] = data
        self[key] = d

    async def set_objects(self, key: str, data):
        await self.set(key, data)

    async def get_object(self, key, field):
        data = await self.get(key)
        return data.get(field)

    async def hlen(self, key):
        return len(self[key])


class RedisCache(aioredis.Redis, ABC):

    def __init__(self, connection):
        self._conn = connection
        super().__init__(self._conn)

    async def get(self, key: str, **kwargs):
        byte = await super().get(key)
        try:
            return pickle.loads(byte)
        except TypeError:
            return

    async def set(self, key: str, data, **kwargs):
        byte = pickle.dumps(data)
        await super().set(key, byte)

    async def remove(self, key: str):
        if await self.exists(key):
            await self.delete(key)

    async def set_object(self, key, field, value):
        byte = pickle.dumps(value)
        await self.hmset(key, field, byte)

    async def set_objects(self, key, dictionary):
        for field, value in dictionary.items():
            byte = pickle.dumps(value)
            dictionary.update({field: byte})
        await self.hmset_dict(key, dictionary)

    async def get_object(self, key, field):
        byte = (await self.hmget(key, field))[0]
        try:
            return pickle.loads(byte)
        except TypeError:
            return
