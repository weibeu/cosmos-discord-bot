from discord.ext import commands

from .. import Cog


async def _moderators_check(ctx):
    guild_profile = await ctx.fetch_guild_profile()
    if not set([role.id for role in ctx.author.roles]) & set(guild_profile.moderators):
        if ctx.author.id not in guild_profile.moderators:
            raise commands.CheckFailure
    return True


def check_mod(**kwargs):

    async def predicate(ctx):
        if not commands.has_permissions(**kwargs):
            if not await _moderators_check(ctx):
                raise commands.CheckFailure
        return True

    return commands.check(predicate)


class Moderation(Cog):

    pass
