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

from .base import CosmosGuildBase


class CosmosGuildPrime(CosmosGuildBase, ABC):

    @property
    def is_prime(self):
        return self.prime_owner and self.prime_owner.is_prime

    def __init__(self, **kwargs):
        self.prime_owner = None
        self.plugin.bot.loop.create_task(self.fetch_prime_owner())

    async def fetch_prime_owner(self):
        self.prime_owner = None
        if document := await self.plugin.bot.get_galaxy("PROFILE").collection.find_one(
                {"prime.guild": self.id}, projection={"user_id": True}
        ):
            self.prime_owner = await self.plugin.bot.profile_cache.get_profile(document.get("user_id"))
