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

from . import time

from discord.ext import commands


class RoleConvertor(commands.Converter):

    async def convert(self, ctx, argument):
        try:
            return [await commands.RoleConverter().convert(ctx, argument)]
        except commands.BadArgument:
            return [await commands.RoleConverter().convert(ctx, raw_role) for raw_role in argument.split()]


class CosmosGuildConverter(commands.Converter):

    async def convert(self, ctx, argument):
        if not (guild := ctx.bot.get_guild(int(argument))):
            raise commands.BadArgument
        return await ctx.bot.guild_cache.get_profile(guild.id)


class CosmosUserProfileConverter(commands.Converter):

    async def convert(self, ctx, argument):
        if not (user := await commands.UserConverter().convert(ctx, argument)):
            raise commands.BadArgument
        return await ctx.bot.profile_cache.get_profile(user.id)


class HumanTimeDeltaConverter(commands.Converter):

    async def convert(self, ctx, argument):
        try:
            return time.HumanDateTimeMixin.from_human_timedelta(argument)
        except ValueError:
            raise commands.BadArgument


class HumanDatetimeConverter(HumanTimeDeltaConverter):

    async def convert(self, ctx, argument):
        argument = argument.lower()
        try:
            if argument.lower().startswith("in"):
                return await super().convert(ctx, argument.lstrip("in "))
            return await super().convert(ctx, argument)
        except (ValueError, commands.BadArgument):
            try:
                return time.HumanDateTimeMixin.from_human(argument)
            except ValueError:
                raise commands.BadArgument


class PrimeTierConverter(commands.Converter):

    async def convert(self, ctx, argument):
        try:
            return ctx.bot.PrimeTier(int(argument))
        except (TypeError, ValueError):
            raise commands.BadArgument
