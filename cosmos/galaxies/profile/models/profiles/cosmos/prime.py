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

from ..base import ProfileModelsBase

from abc import ABC
from enum import Enum


class CosmosPrimeTier(Enum):

    NONE = 0
    NEUTRINO = 1
    QUARK = 5
    STRING = 15


class CosmosPrime(ProfileModelsBase, ABC):

    @property
    def is_prime(self):
        return self.prime_tier >= CosmosPrimeTier.QUARK

    def __init__(self, **kwargs):
        self.prime_tier = kwargs.get("prime_tier", CosmosPrimeTier.NONE)

    async def make_prime(self, tier=CosmosPrimeTier.QUARK, make=True):
        self.prime_tier = tier if make else CosmosPrimeTier.NONE

        await self.collection.update_one(
            self.document_filter, {"$set": {"prime_tier": self.prime_tier.value}})
