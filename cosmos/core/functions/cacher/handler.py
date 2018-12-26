from . import cachers


class CacheHandler(object):

    def __init__(self, bot):
        self.bot = bot
        self.dict = None
        self.ttl = None
        self.lru = None
        self.lfu = None
        self.redis = None
        self.bot.loop.create_task(self.__fetch_cachers())

    async def __fetch_cachers(self):
        self.dict = cachers.DictCache()
        self.ttl = cachers.TTLCache()
        self.lru = cachers.LRUCache()
        self.lfu = cachers.LFUCache()
        self.redis = cachers.RedisCache()
        try:
            await self.redis._fetch_client()
        except OSError:
            self.bot.log.error("Unable to connect to redis server. Check if it's running.")
            self.bot.log.info("Using cachers.AsyncDictCache instead.")
            self.bot.log.warning("Most of the functions of web client will not work.")
            self.bot.eh.sentry.capture_exception()
            self.redis = cachers.AsyncDictCache()   # Temporarily use normal dictionary if can't reach redis servers.
