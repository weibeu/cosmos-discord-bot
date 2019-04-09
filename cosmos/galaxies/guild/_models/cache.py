from .guild_profile import CosmosGuild


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

    async def get_profile(self, guild_id) -> CosmosGuild:
        # profile = await self.redis.get_object(self.collection.name, guild_id)
        profile = self.lru.get(guild_id)
        if not profile:
            profile_document = (await self.collection.find_one(
                {"guild_id": guild_id}, projection=self.DEFAULT_PROJECTION))
            if not profile_document:
                profile_document = {"guild_id": guild_id}
                await self.collection.insert_one(profile_document)
            profile = CosmosGuild.from_document(self.plugin, profile_document)
            # await self.redis.set_object(self.collection.name, guild_id, profile)
            self.lru.set(guild_id, profile)
        return profile

    async def __precache_prefixes(self):
        async for document in self.collection.find({}, {"prefixes": True, "guild_id": True, "_id": False}):
            prefixes = document.get("prefixes")
            if prefixes:
                self.prefixes.set(document["guild_id"], prefixes)
