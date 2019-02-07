import asyncio

from pymongo import UpdateOne
from pymongo.errors import InvalidOperation
from .user_profile import CosmosUserProfile


class ProfileCache(object):

    def __init__(self, plugin):
        self.plugin = plugin
        self.bot = self.plugin.bot
        self._redis = None
        self.lfu = self.bot.cache.lfu(self.plugin.data.profile.cache_max_size)
        self.__collection_name = self.plugin.data.profile.collection_name
        self.collection = self.bot.db[self.__collection_name]
        self.bot.loop.create_task(self.__update_database())
        # self.bot.loop.create_task(self.__get_redis_client())

    async def __get_redis_client(self):
        await self.bot.wait_until_ready()
        self._redis = self.bot.cache.redis

    async def prepare(self):
        self.bot.log.info("Preparing profile caches.")
        # await self.__get_redis_client()
        profile_documents = dict()
        profiles_data = await self.collection.find({}).to_list(self.plugin.data.profile.cache_max_size)
        for profile_document in profiles_data:
            profile = CosmosUserProfile.from_document(self.plugin, profile_document)
            user_id = int(profile_document.get("user_id"))  # bson.int64.Int64 to int
            profile_documents[user_id] = profile
        # await self._redis.set_objects(self.__collection_name, profile_documents)
        self.lfu.update(profile_documents)
        # profile_count = await self._redis.hlen(self.__collection_name)
        profile_count = self.lfu.currsize
        self.bot.log.info(f"Loaded {profile_count} profiles to cache.")

    async def get_profile(self, user_id: int) -> CosmosUserProfile:
        # profile = await self._redis.get_object(self.__collection_name, user_id)
        profile = self.lfu.get(user_id)
        if not profile:
            profile_document = await self.collection.find_one({"user_id": user_id})
            if profile_document:
                profile = CosmosUserProfile.from_document(self.plugin, profile_document)
                # await self._redis.set_object(self.__collection_name, user_id, profile)
                self.lfu.set(user_id, profile)
        return profile

    async def create_profile(self, user_id: int) -> CosmosUserProfile:
        profile_document = self.plugin.data.profile.document_schema.copy()
        profile_document.update({"user_id": user_id})
        await self.collection.insert_one(profile_document)
        return await self.get_profile(user_id)

    async def give_xp(self, message):
        profile = await self.get_profile(message.author.id)
        if not profile:
            embed = self.bot.theme.embeds.one_line.primary(f"Welcome {message.author.name}. Creating your profile!")
            await message.channel.send(embed=embed)
            profile = await self.create_profile(message.author.id)
        if profile.in_xp_buffer:
            return

        await profile.give_xp()

    async def __update_database(self):
        while True:
            await asyncio.sleep(self.plugin.data.profile.update_task_cooldown)
            self.bot.log.info("Updating Profile caches to database.")
            batch = [UpdateOne(*profile.to_update_document()) for profile in self.lfu.values()]
            # TODO: Make global database batches.
            try:
                result = await self.collection.bulk_write(batch, ordered=False)
                self.bot.log.info(f"Job completed. Updated {result.modified_count} profiles.")
            except InvalidOperation:
                self.bot.eh.sentry.capture_exception()
