from ._models import ModerationAction, actions
from discord.ext import commands

import discord

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

    def __init__(self, plugin):
        self.plugin = plugin
        super().__init__()

    @Cog.command(name="warn")
    @check_mod(kick_members=True)
    async def warn(self, ctx, member: discord.Member, *, reason=None):
        action = ModerationAction(ctx, actions.Warned, member, reason)
        try:
            await action.warn(f"⚠    You were warned in {ctx.guild.name}.")
            res = f"✅    {member.name} has been warned."
        except discord.HTTPException:
            res = f"✅    Failed to warn {member.name}. Warning logged."
        finally:
            profile = await ctx.fetch_member_profile()
            _id = await self.bot.discordDB.set(action.document)
            await profile.add_warning(_id)
        await ctx.send_line(res)
