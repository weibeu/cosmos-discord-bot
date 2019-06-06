import typing
import discord

from .. import Cog

from discord.ext import commands


class AdministratorSettings(Cog):

    async def cog_check(self, ctx):
        if not ctx.author.guild_permissions.administrator:
            raise commands.MissingPermissions(["administrator"])
        return True

    @Cog.group(name="moderators", aliases=["moderator", "mod", "mods"])
    async def moderators(self, ctx):
        pass

    @moderators.command(name="add")
    async def add_moderator(self, ctx, moderator: typing.Union[discord.Role, discord.Member]):
        if not await ctx.confirm():
            return
        guild_profile = await ctx.fetch_guild_profile()
        if moderator.id in guild_profile.moderators:
            return await ctx.send_line(f"❌    {moderator.name} already exists in server's moderators.")

        await guild_profile.add_moderator(moderator.id)
        await ctx.send_line(f"✅    {moderator.name} has been added to server's moderators.")

    @moderators.command(name="remove")
    async def remove_moderator(self, ctx, moderator: typing.Union[discord.Role, discord.Member]):
        if not await ctx.confirm():
            return
        guild_profile = await ctx.fetch_guild_profile()
        if moderator.id not in guild_profile.moderators:
            return await ctx.send_line("❌    They are not server's moderator yet.")

        await guild_profile.remove_moderator(moderator.id)
        await ctx.send_line(f"✅    {moderator.name} has been removed from server's moderators.")
