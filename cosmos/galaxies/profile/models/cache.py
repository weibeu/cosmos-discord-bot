import asyncio
import random

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

        xp_buffer_max_size = self.plugin.data.profile.xp_buffer_max_size
        xp_buffer_cooldown = self.plugin.data.profile.xp_buffer_cooldown
        self.__xp_buffer = self.bot.cache.ttl(xp_buffer_max_size, xp_buffer_cooldown)

    async def __get_redis_client(self):
        await self.bot.wait_until_ready()
        self._redis = self.bot.cache.redis

    async def prepare(self):
        self.bot.log.info("Preparing profile caches.")
        # await self.__get_redis_client()
        profile_documents = dict()
        profiles_data = await self.collection.find({}).to_list(None)
        for profile_document in profiles_data:
            profile = CosmosUserProfile.from_document(profile_document)
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
                profile = CosmosUserProfile.from_document(profile_document)
                # await self._redis.set_object(self.__collection_name, user_id, profile)
                self.lfu.set(user_id, profile)
        return profile

    async def create_profile(self, user_id: int) -> CosmosUserProfile:
        profile_document = self.plugin.data.profile.document_schema
        profile_document.update({"user_id": user_id})
        await self.collection.insert_one(profile_document)
        return await self.get_profile(user_id)

    async def give_xp(self, message):
        if message.author.id in self.__xp_buffer:
            return
        profile = await self.get_profile(message.author.id)
        xp = random.randint(self.plugin.data.profile.xp_default_min, self.plugin.data.profile.xp_default_max)
        if not profile:
            embed = self.bot.theme.embeds.one_line.primary("Welcome to Cosmos. Creating your profile!")
            await message.channel.send(content=message.author.mention, embed=embed)
            profile = await self.create_profile(message.author.id)
        profile.give_xp(xp)
        self.__xp_buffer.set(message.author.id, None)    # TODO: Replace None or convert xp_buffer to list or set.

    async def get_profile_embed(self, ctx):
        profile = await self.get_profile(ctx.author.id)
        if not profile:
            profile = await self.create_profile(ctx.author.id)
        embed = self.bot.theme.embeds.primary(title="Cosmos Profile")
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
        embed.add_field(name="Reputation points", value=str(profile.reps))
        embed.add_field(name="Level", value=str(profile.level))
        embed.add_field(name="Experience points", value=str(profile.xp))
        embed.add_field(name="Experience points required for next level", value=str(profile.delta_xp))
        description = profile.description or self.plugin.data.profile.default_description
        embed.add_field(name="Profile description", value=description)
        return embed

    async def __update_database(self):
        while True:
            await asyncio.sleep(self.plugin.data.profile.update_task_cooldown)
            self.bot.log.info("Updating Profile caches to database.")
            batch = [UpdateOne(*profile.to_xp_filter_and_update()) for profile in self.lfu.values()]
            try:
                result = await self.collection.bulk_write(batch, ordered=False)
                self.bot.log.info(f"Job completed. Updated {result.modified_count} profiles.")
            except InvalidOperation:
                self.bot.eh.sentry.capture_exception()
