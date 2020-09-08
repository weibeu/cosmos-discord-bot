"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from abc import ABC, abstractmethod

import pickle
import aioredis
import itertools
import cachetools


class _CacheBase(ABC):

    @abstractmethod
    def __setitem__(self, key, value):
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, item):
        raise NotImplementedError

    @abstractmethod
    def __delitem__(self, key):
        raise NotImplementedError

    @abstractmethod
    def __iter__(self):
        raise NotImplementedError

    @abstractmethod
    def __len__(self):
        raise NotImplementedError


class Cache(_CacheBase):

    PERMANENT_ATTRIBUTE = "_cache_permanent_persist_"

    def __repr__(self):
        return f"PERMANENT={repr(self.__permanent_elements)} | CACHE={super().__repr__()}"

    def _is_permanent(self, value):
        return bool(getattr(value, self.PERMANENT_ATTRIBUTE, False))

    def getsizeof(self, value):
        return 0 if self._is_permanent(value) else 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__permanent_elements = dict()

    def __setitem__(self, key, value):
        if not self._is_permanent(value):
            return super().__setitem__(key, value)
        self.__permanent_elements[key] = value

    def __getitem__(self, key):
        if not self._is_permanent(self.__permanent_elements.get(key)):
            return super().__getitem__(key)
        return self.__permanent_elements[key]

    def __delitem__(self, key):
        if not self._is_permanent(self.__permanent_elements.get(key)):
            return super().__delitem__(key)
        del self.__permanent_elements[key]

    def __contains__(self, key):
        return super().__contains__(key) or key in self.__permanent_elements

    def __iter__(self):
        return itertools.chain(iter(self.__permanent_elements), super().__iter__())

    def __len__(self):
        return super().__len__() + len(self.__permanent_elements)

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

    pass


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
