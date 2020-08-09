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

from cosmos import exceptions

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

    async def get_profile(self, guild_id) -> CosmosGuild:
        if not self.bot.get_guild(guild_id):
            raise exceptions.GuildNotFoundError(guild_id)
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
