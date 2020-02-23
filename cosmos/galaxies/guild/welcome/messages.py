import typing
import discord

from .base import WelcomeBase


class WelcomeMessage(WelcomeBase):
    """A plugin to send customized welcome messages for newly joined members."""

    @WelcomeBase.welcome.group(name="message", aliases=["msg"], invoke_without_command=True)
    async def welcome_message(self, ctx):
        """Displays the template being used for Welcome Messages if it has been set already."""
        if not ctx.guild_profile.welcome_message:
            return await ctx.send_line(f"❌    Welcome Message has not been set in the server.")
        embed = ctx.embed_line("Welcome Message Template", ctx.guild.icon_url)
        embed.description = f"```css\n{ctx.guild_profile.welcome_message}```"

    @welcome_message.command(name="set")
    async def set_welcome_message(self, ctx, channel: typing.Optional[discord.TextChannel] = None, *, message):
        """Setup and enable Welcome Messages using provided template. The Welcome Messages are sent to the current or
        any specified channel whenever a new user joins the server.

        """
        channel = channel or ctx.channel
        await ctx.guild_profile.set_welcome_message(message, channel)
        await ctx.send_line(f"✅    Welcome messages has been set in {channel} channel.")

    @welcome_message.command(name="remove", aliases=["delete"])
    async def remove_welcome_message(self, ctx):
        """Remove and disable Welcome Messages from the server."""
        if not await ctx.confirm():
            return
        await ctx.guild_profile.remove_welcome_message()
        await ctx.send_line(f"✅    Welcome messages has been disabled and removed.")

    @WelcomeBase.welcome.group(name="directmessage", aliases=["dm", "directmsg"], invoke_without_command=True)
    async def direct_message(self, ctx):
        """Displays the template being using for Direct Welcome Messages if it has been set already."""
        if not ctx.guild_profile.direct_welcome_message:
            return await ctx.send_line(f"❌    Direct Welcome Messages has not been set in the server.")
        embed = ctx.embed_line("Direct Welcome Message Template", ctx.guild.icon_url)
        embed.description = f"```css\n{ctx.guild_profile.direct_welcome_message}```"

    @direct_message.command(name="set")
    async def set_direct_welcome_message(self, ctx, message):
        """Setup and enable Direct Welcome Messages using provided template. The Welcome Messages are sent as direct
         message whenever a new user joins the server.

        """
        await ctx.guild_profile.set_direct_welcome_message(message)
        await ctx.send_line(f"✅    Direct Message welcome messages has been set.")

    @direct_message.command(name="remove", aliases=["delete"])
    async def remove_direct_welcome_message(self, ctx):
        """Remove and disable Direct Welcome Messages from the server."""
        if not await ctx.confirm():
            return
        await ctx.guild_profile.remove_direct_welcome_message()
        await ctx.send_line(f"✅    Direct Message welcome messages has been disabled and removed.")
