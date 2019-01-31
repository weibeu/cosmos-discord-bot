from .user_profile import CosmosUserProfile


class ProfileCache(object):

    def __init__(self, plugin):
        self.plugin = plugin
        self.bot = self.plugin.bot
        self._redis = self.bot.cache.redis
        self.__collection_name = self.plugin.data.profile.collection_name
        self.collection = self.bot.db[self.__collection_name]

    async def prepare(self):
        self.bot.log.info("Preparing profile caches.")
        profiles = dict()
        profiles_data = await self.collection.find({}).to_list(None)
        for profile_document in profiles_data:
            profile = CosmosUserProfile.from_document(profile_document)
            profiles[profile_document["user_id"]] = profile
        await self._redis.hmset_dict(self.__collection_name, profiles)
        self.bot.log.info(f"Loaded {len(profiles)} to cache.")

    async def get_profile(self, user_id: int):
        profile = await self._redis.hget(self.__collection_name, user_id)
        if not profile:
            profile_document = await self.collection.find_one({"user_id": user_id})
            if profile_document:
                profile = CosmosUserProfile.from_document(profile_document)
        return profile
