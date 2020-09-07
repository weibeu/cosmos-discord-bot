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

from discord.ext import commands

from ...exceptions import UserNotPrime
from ...exceptions import GuildNotPrime


class CosmosChecks(object):

    @classmethod
    def prime_user(cls):
        async def predicate(ctx):
            if not (await ctx.bot.profile_cache.get_profile(ctx.author.id)).is_prime:
                raise UserNotPrime
            return True

        return commands.check(predicate)

    @classmethod
    def prime_guild(cls):
        async def predicate(ctx):
            if not (await ctx.bot.guild_cache.get_profile(ctx.guild.id)).is_prime:
                raise GuildNotPrime
            return True
        return commands.check(predicate)

    @classmethod
    def check_user(cls, user_id):
        async def predicate(ctx):
            if ctx.author.id == user_id:
                return True
            return False

        return commands.check(predicate)
