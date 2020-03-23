from cosmos.core.utilities import converters, Utility

import discord
import random

from ... import Cog
from discord.ext import commands


class SecretConfessions(Cog):
    """A plugin to spice up your community with secret confessions. It lets the members to confess anonymously in
    certain channel.

    """

    FACE_EMOTES = [
        '😀', '😃', '😄', '😁', '😆', '😅', '😂', '🤣', '☺️', '😊', '😇', '🙂', '🙃', '😉', '😌', '😍',
        '\U0001f970', '😘', '😗', '😙', '😚', '😋', '😛', '😝', '😜', '\U0001f92a', '\U0001f928',
        '\U0001f9d0', '🤓', '😎', '\U0001f929', '\U0001f973', '😏', '😒', '😞', '😔', '😟', '😕', '🙁',
        '☹️', '😣', '😖', '😫', '😩', '\U0001f97a', '😢', '😭', '😤', '😠', '😡', '\U0001f92c',
        '\U0001f92f', '😳', '\U0001f975', '\U0001f976', '😱', '😨', '😰', '😥', '😓', '🤗', '🤔',
        '\U0001f92d', '\U0001f971', '\U0001f92b', '🤥', '😶', '😐', '😑', '😬', '🙄', '😯', '😦', '😧',
        '😮', '😲', '😴', '🤤', '😪', '😵', '🤐', '\U0001f974', '🤢', '\U0001f92e', '🤧', '😷', '🤒', '🤕',
        '🤑', '🤠', '😈', '👿', '👹', '👺', '🤡', '💩', '👻', '💀', '☠️', '👽', '👾', '🤖', '😺', '😸',
        '😹', '😻', '😼', '😽', '🙀', '😿', '😾'
    ]

    @Cog.cooldown(1, 420, Cog.bucket_type.user)
    @Cog.group(name="confessions", aliases=["confession", "confess"], invoke_without_command=True)
    async def confessions(self, ctx, guild_profile: converters.CosmosGuildConverter, *, confession):
        """Lets you confess anonymously in specified server. Your identity might be visible to the server moderators.
        You can make only one confession every 7 minutes.

        """
        if ctx.guild:
            raise commands.CheckFailure
        if ctx.author not in guild_profile.guild.members:
            return await ctx.send_line(f"❌    You can't make confession in server you're not in.")
        if not guild_profile.confessions_channel:
            return await ctx.send_line(f"❌    Secret confessions isn't enabled in {guild_profile.guild.name}.")
        embed = ctx.embed_line(f"{random.choice(self.FACE_EMOTES)}    {Utility.get_random_strings(27)}"
                               f"#{random.randint(0000, 9999)}")
        embed.description = confession
        await guild_profile.confessions_channel.send(embed=embed)
        await ctx.send_line(f"✅    Your confession has been posted in {guild_profile.guild.name}.")

    @confessions.command(name="set", aliases=["setup", "enable"])
    @commands.has_permissions(manage_guild=True)
    async def set_confessions(self, ctx, channel: discord.TextChannel = None):
        """Set secret confessions to current or specified channel."""
        channel = channel or ctx.channel
        guild_profile = await ctx.fetch_guild_profile()
        await guild_profile.set_confessions_channel(channel)
        await ctx.send_line(f"✅    Secret confessions has been set in {channel}.")

    @confessions.command(name="remove", aliases=["delete", "disable"])
    @commands.has_permissions(manage_guild=True)
    async def remove_secret_confessions(self, ctx):
        """Remove secret confessions from the server."""
        guild_profile = await ctx.fetch_guild_profile()
        await guild_profile.remove_confessions_channel()
        await ctx.send_line(f"✅    Secret confessions has been removed.")
