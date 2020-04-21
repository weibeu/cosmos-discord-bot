from .guild_profile import CosmosGuild
from pymongo.errors import DuplicateKeyError


class GuildCache(object):

    DEFAULT_PROJECTION = {
        "prefixes": False
    }

    def __init__(self, plugin):
        self.plugin = plugin
        self.bot = self.plugin.bot
        self.collection = self.plugin.collection
        self.lru = self.bot.cache.lru()
        # self.redis = None
        # self.bot.loop.create_task(self.__fetch_redis_client())

        self.prefixes = self.bot.cache.dict()
        self.bot.loop.create_task(self.__precache_prefixes())

    async def __fetch_redis_client(self):
        await self.bot.wait_until_ready()
        self.redis = self.bot.cache.redis

    async def get_profile(self, guild_id):
        if not self.bot.get_guild(guild_id):
            return
        # profile = await self.redis.get_object(self.collection.name, guild_id)
        profile = self.lru.get(guild_id)
        if not profile:
            profile_filter = {"guild_id": guild_id}
            profile_document = (await self.collection.find_one(profile_filter, projection=self.DEFAULT_PROJECTION))
            if profile_document:
                profile = CosmosGuild.from_document(self.plugin, profile_document)
                self.lru.set(guild_id, profile)
            else:
                profile = CosmosGuild.from_document(self.plugin, profile_filter)
                self.lru.set(guild_id, profile)
                await self.create_profile(profile_filter)
        return profile

    # TODO: Find a way to call create_profile. It gets invoked several times at the same instant under get_profile.

    async def create_profile(self, profile_filter):
        if not await self.collection.find_one(profile_filter):
            # To handle rare cases when this method still gets invoked multiple times.
            # !! TODO: It still gets invoked so many times. Temp fix: create primary index for guild_id in guilds.
            try:
                await self.collection.insert_one(profile_filter)
            except DuplicateKeyError:
                pass

    async def __precache_prefixes(self):
        async for document in self.collection.find({}, {"prefixes": True, "guild_id": True, "_id": False}):
            prefixes = document.get("prefixes")
            if prefixes:
                self.prefixes.set(document["guild_id"], prefixes)
