from cosmos.core.functions.cacher import cachers


class Cache(object):

    def __init__(self, bot):
        self.bot = bot
        self.dict = None
        self.ttl = None
        self.lru = None
        self.lfu = None
        self.__fetch_cachers()

    def __fetch_cachers(self):
        self.dict = cachers.DictCache
        self.ttl = cachers.TTLCache
        self.lru = cachers.LRUCache
        self.lfu = cachers.LFUCache

    def get_cache(self, cache_type: str):
        return getattr(self, cache_type, default=None) or getattr(cachers, cache_type, default=None)
