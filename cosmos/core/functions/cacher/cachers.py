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

import aioredis
import pickle
import itertools
import cachetools

from abc import ABC
from collections.abc import MutableMapping


class Cache(MutableMapping):

    PERMANENT_ATTRIBUTE = "_cache_permanent_persist_"

    def _is_permanent(self, value):
        return bool(getattr(value, self.PERMANENT_ATTRIBUTE, False))

    def getsizeof(self, value):
        return 0 if self._is_permanent(value) else 1

    def __init__(self, *args, **kwargs):
        self.__permanent_elements = dict()

    def __repr__(self):
        return f"<PERMANENT={repr(self.__permanent_elements)} | CACHE={super().__repr__()}>"

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

    def set(self, key: str or int, data):
        self.update({key: data})

    def get(self, key: str or int, default=None):
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def pop(self, key, default=None):
        try:
            if not self._is_permanent(self.__permanent_elements.get(key)):
                return super().pop(key)
            return self.__permanent_elements.pop(key)
        except KeyError:
            return default

    def remove(self, key: str or int):
        self.pop(key)


class DictCache(dict, Cache):

    pass


class TTLCache(Cache, cachetools.TTLCache, ABC):

    def __init__(self, max_size: int = 50000, ttl: int = 60, **kwargs):
        Cache.__init__(self, **kwargs)
        cachetools.TTLCache.__init__(self, max_size, ttl, **kwargs)


class LRUCache(Cache, cachetools.LRUCache, ABC):

    def __init__(self, max_size: int = 50000, **kwargs):
        Cache.__init__(self, **kwargs)
        cachetools.LRUCache.__init__(self, max_size, **kwargs)


class LFUCache(Cache, cachetools.LFUCache, ABC):

    def __init__(self, max_size: int = 50000, **kwargs):
        Cache.__init__(self, **kwargs)
        cachetools.LFUCache.__init__(self, max_size, **kwargs)


class AsyncDictCache(DictCache, ABC):

    def __init__(self):
        super().__init__()

    async def get(self, key: str, default=None):
        # byte = super().get(key)
        # if byte:
        #    data = pickle.loads(byte)
        # else:
        #    data = None
        return super().get(key, default=default)

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
