import typing

import discord

from discord.ext import commands
from .._models import GuildBaseCog


class Reactor(GuildBaseCog):

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
    @commands.has_permissions(manage_guild=True)
    async def _reactor(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        reactor = ctx.guild_profile.reactors.get_reactor(channel.id)
        if not reactor:
            return await ctx.send_line(f"❌    There's no reactor enabled in #{channel} yet.")
        embed = ctx.embeds.one_line.primary(f"#{channel.name} Reactor", ctx.guild.icon_url)
        embed.description = "**Emotes:** " + " ".join([str(emote) for emote in reactor.emotes])
        await ctx.send(embed=embed)

    @_reactor.command(name="setup", aliases=["set"])
    async def set_reactor(
            self, ctx, channel: typing.Optional[discord.TextChannel] = None, *emotes: typing.Union[discord.Emoji, str]):
        channel = channel or ctx.channel
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
        channel = channel or ctx.channel
        if not ctx.guild_profile.reactors.get_reactor(channel.id):
            return await ctx.send_line(f"❌    There's no reactor enabled in #{channel} yet.")
        if await ctx.confirm(f"⚠    Are you sure to remove the reactor from #{channel}?"):
            await ctx.guild_profile.reactors.remove_reactor(channel)
            await ctx.send_line(f"✅    Reactor was removed from #{channel}.")

    @_reactor.command(name="enable", aliases=["on"])
    async def enable_reactor(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        reactor = ctx.guild_profile.reactors.get_reactor(channel.id)
        if not reactor:
            return await ctx.send_line(f"❌    There's no reactor enabled in #{channel} yet.")
        await ctx.guild_profile.reactors.enable_reactor(reactor)
        await ctx.send_line(f"✅    Reactor was enabled in #{channel}.")

    @_reactor.command(name="disable", aliases=["off"])
    async def disable_reactor(self, ctx, channel: discord.TextChannel = None):
        channel = channel or ctx.channel
        reactor = ctx.guild_profile.reactors.get_reactor(channel.id)
        if not reactor:
            return await ctx.send_line(f"❌    There's no reactor enabled in #{channel} yet.")
        await ctx.guild_profile.reactors.enable_reactor(reactor, enabled=False)
        await ctx.send_line(f"✅    Reactor was disabled in #{channel}.")
