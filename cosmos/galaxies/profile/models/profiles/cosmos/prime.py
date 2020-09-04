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
        self.prime_tier = kwargs.get("tier", self.plugin.bot.PrimeTier.NONE)
        self.prime_guild = None
        self.plugin.bot.loop.create_task(self.__fetch_prime_guild(kwargs.get("guild")))

    async def __fetch_prime_guild(self, guild_id):
        self.prime_guild = await self.plugin.bot.guild_cache.get_profile(guild_id) if guild_id else None

    async def make_prime(self, tier=None, guild_id=None):
        self.prime_tier = tier or self.plugin.bot.PrimeTier.QUARK
        await self.__fetch_prime_guild(guild_id)

        update = {"prime.guild": self.prime_guild.id} if self.prime_guild else dict()
        update.update({"prime.tier": self.prime_tier.value})
        await self.collection.update_one(self.document_filter, {"$set": update})

    async def remove_prime(self):
        self.prime_tier = self.plugin.bot.PrimeTier.FORMER
        self.prime_guild = None

        await self.collection.update_one(self.document_filter, {"$set": {
            "prime.tier": self.prime_tier.value,
            "prime.guild": self.prime_guild
        }})
