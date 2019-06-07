from discord.ext import commands

from .. import Cog


async def _has_permissions(ctx, perms):
    ch = ctx.channel
    permissions = ch.permissions_for(ctx.author)

    if [perm for perm, value in perms.items() if getattr(permissions, perm, None) != value]:
        return False

    return True


async def _moderators_check(ctx):
    guild_profile = await ctx.fetch_guild_profile()
    if not set([role.id for role in ctx.author.roles]) & set(guild_profile.moderators):
        if ctx.author.id not in guild_profile.moderators:
            raise commands.CheckFailure
    return True


def check_mod(**perms):

    async def predicate(ctx):
        if not await _has_permissions(ctx, perms) and not await _moderators_check(ctx):
            raise commands.CheckFailure
        return True

    return commands.check(predicate)


class Moderation(Cog):

    pass
