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
            conn = await aioredis.connection.create_connection("redis://localhost", loop=self.bot.loop)
            self.redis = cachers.RedisCache(conn)
        except OSError:
            self.bot.log.debug("Unable to connect to redis server. Check if it's running.")
            self.bot.log.debug("Using cachers.AsyncDictCache instead.")
            self.bot.log.debug("Most of the functions of web client will not work.")
            self.redis = cachers.AsyncDictCache()   # Temporarily use normal dictionary if can't reach redis servers.
