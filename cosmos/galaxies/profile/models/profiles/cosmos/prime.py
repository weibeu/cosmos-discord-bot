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

from abc import ABC

from ..base import ProfileModelsBase


class CosmosUserPrime(ProfileModelsBase, ABC):

    @property
    def is_prime(self):
        return self.prime_tier >= self.plugin.bot.PrimeTier.QUARK

    def __init__(self, **kwargs):
        self.prime_tier = self.plugin.bot.PrimeTier(kwargs.get("tier", 0))
        self.prime_guild = None
        self.plugin.bot.loop.create_task(self.__fetch_prime_guild(kwargs.get("guild")))

    async def __fetch_prime_guild(self, guild_id):
        if not guild_id:
            return
        self.prime_guild = await self.plugin.bot.guild_cache.get_profile(guild_id)

    async def __update_prime_guild_state(self):
        try:
            await self.prime_guild.fetch_prime_owner()
        except AttributeError:
            pass

    def __garbage_collect(self):
        self.plugin.bot.profile_cache.lfu.remove(self.id)

    async def make_prime(self, tier=None, guild_id=None):
        tier = tier or self.plugin.bot.PrimeTier.QUARK
        await self.__fetch_prime_guild(guild_id)

        update = {"prime.guild": self.prime_guild.id} if self.prime_guild else dict()
        update.update({"prime.tier": tier.value})
        await self.collection.update_one(self.document_filter, {"$set": update})

        self.__garbage_collect()
        await self.__update_prime_guild_state()

    # Maybe or maybe not remove the user from permanent cache when their prime sub ends.
    # Problem is when their prime sub ends, they will still exist in permanent cache with __cache_permanent_persist_
    # flag set to False. Since its set to False, cache will try to return it from the actual cache. But certainly
    # it won't exist there. Apparently this situation can happen vice-versa as well.

    async def remove_prime(self):
        tier = self.plugin.bot.PrimeTier.FORMER

        await self.collection.update_one(self.document_filter, {"$set": {
            "prime.tier": tier.value,
            "prime.guild": None
        }})

        self.__garbage_collect()
        await self.__update_prime_guild_state()
