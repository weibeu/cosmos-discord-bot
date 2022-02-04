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

from . import cachers


class CacheHandler(object):

    def __init__(self, bot):
        self.bot = bot
        self.redis = None
        self.dict = cachers.DictCache
        self.ttl = cachers.TTLCache
        self.lru = cachers.LRUCache
        self.lfu = cachers.LFUCache
        self.bot.loop.create_task(self.__fetch_redis_client())

    async def __fetch_redis_client(self):
        try:
            conn = await aioredis.from_url("redis://localhost", loop=self.bot.loop)
            self.redis = cachers.RedisCache(conn)
        except OSError:
            # self.bot.log.debug("Unable to connect to redis server. Check if it's running.")
            # self.bot.log.debug("Using cachers.AsyncDictCache instead.")
            # self.bot.log.debug("Most of the functions of web client will not work.")
            self.redis = cachers.AsyncDictCache()   # Temporarily use normal dictionary if can't reach redis servers.
