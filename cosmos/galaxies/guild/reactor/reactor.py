import typing

import discord

from discord.ext import commands
from .._models import GuildBaseCog


class Reactor(GuildBaseCog):
    """A utility plugin to automatically add reactions to message sent in text channels."""

    INESCAPABLE = False

    async def cog_check(self, ctx):
        await super().cog_check(ctx)
        if not ctx.author.guild_permissions.manage_guild:
            raise commands.MissingPermissions(["manage_guild"])
        return True

    @GuildBaseCog.listener()
    async def on_message(self, message):
        if not message.guild:
            return
        guild_profile = await self.plugin.cache.get_profile(message.guild.id)
        if not guild_profile.reactors:
            return
        reactor = guild_profile.reactors.get_reactor(message.channel.id)
        if not reactor or not reactor.enabled:
            return

        for emote in reactor.emotes:
            await message.add_reaction(emote)

    @GuildBaseCog.group(name="reactor", aliases=["reactors"], invoke_without_command=True)
    async def _reactor(self, ctx, channel: discord.TextChannel = None):
        """Displays reactor settings of current or specified channel."""
        channel = channel or ctx.channel
        reactor = ctx.guild_profile.reactors.get_reactor(channel.id)
        if not reactor:
            return await ctx.send_line(f"❌    There's no reactor enabled in #{channel} yet.")
        embed = ctx.embeds.one_line.primary(f"#{channel.name} Reactor", ctx.guild.icon_url)
        embed.description = "**Emotes:** " + " ".join([str(emote) for emote in reactor.emotes])
        await ctx.send(embed=embed)

    @_reactor.command(name="set", aliases=["setup"])
    @commands.bot_has_permissions(add_reactions=True, external_emojis=True)
    async def set_reactor(
            self, ctx, channel: typing.Optional[discord.TextChannel] = None, *emotes: typing.Union[discord.Emoji, str]):
        """Setup reactor in current or specified channel using provided emotes. You can only use the emotes which
        the bot can see. It enables reactors just after this setup is complete.

        """
        channel = channel or ctx.channel
        if not channel.permissions_for(ctx.me).add_reactions:
            return await ctx.send_line(f"❌    Please permit me to add reactions in {channel} first.")
        test_message = await ctx.send_line(f"👇    This is how bot will react to messages in #{channel}.")
        for emote in emotes:
            try:
                await test_message.add_reaction(emote)
            except discord.NotFound:
                return await ctx.send_line("❌    Please make sure to use emotes which I have access to.")
            except discord.HTTPException:
                return await ctx.send_line("❌    Please provide valid emotes supported by Discord.")
        if await ctx.confirm(f"❓    Are you sure to set and enable those reactions in #{channel}?"):
            await ctx.guild_profile.reactors.set_reactor(channel, emotes)
            await ctx.send_line(f"✅    Reactor enabled in #{channel}.")

    @_reactor.command(name="remove", aliases=["delete"])
    async def remove_reactor(self, ctx, channel: discord.TextChannel = None):
        """Removes any reactor set in current or specified channel."""
        channel = channel or ctx.channel
        if not ctx.guild_profile.reactors.get_reactor(channel.id):
            return await ctx.send_line(f"❌    There's no reactor enabled in #{channel} yet.")
        if await ctx.confirm(f"⚠    Are you sure to remove the reactor from #{channel}?"):
            await ctx.guild_profile.reactors.remove_reactor(channel)
            await ctx.send_line(f"✅    Reactor was removed from #{channel}.")

    @_reactor.command(name="enable", aliases=["on"])
    async def enable_reactor(self, ctx, channel: discord.TextChannel = None):
        """Enable reactor if it was set of current or specified channel."""
        channel = channel or ctx.channel
        if not channel.permissions_for(ctx.me).add_reactions:
            return await ctx.send_line(f"❌    Please permit me to add reactions in {channel} first.")
        reactor = ctx.guild_profile.reactors.get_reactor(channel.id)
        if not reactor:
            return await ctx.send_line(f"❌    There's no reactor enabled in #{channel} yet.")
        await ctx.guild_profile.reactors.enable_reactor(reactor)
        await ctx.send_line(f"✅    Reactor was enabled in #{channel}.")

    @_reactor.command(name="disable", aliases=["off"])
    async def disable_reactor(self, ctx, channel: discord.TextChannel = None):
        """Disable reactor from current or specified channel."""
        channel = channel or ctx.channel
        reactor = ctx.guild_profile.reactors.get_reactor(channel.id)
        if not reactor:
            return await ctx.send_line(f"❌    There's no reactor enabled in #{channel} yet.")
        await ctx.guild_profile.reactors.enable_reactor(reactor, enabled=False)
        await ctx.send_line(f"✅    Reactor was disabled in #{channel}.")
