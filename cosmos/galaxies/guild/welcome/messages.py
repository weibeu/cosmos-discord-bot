from .base import WelcomeBase, MessageTemplateMember

import re
import typing
import discord

from discord.ext import commands


class InvalidVariable(commands.BadArgument):

    pass


class Template(commands.Converter):

    async def convert(self, ctx, argument):
        if set(re.findall(r"{([^}]+)\}", argument)) - set(MessageTemplateMember.__slots__):
            raise InvalidVariable
        return argument


class WelcomeMessage(WelcomeBase):
    """A plugin to send customized welcome messages for newly joined members.
    Lets you set fully customized template to use for Welcome Messages using different variables. Use `{variable}` in
    your template to use the variables.

    Valid Variables:
        - {id} -- Discord ID of the member.
        - {mention} -- Mentions the member.
        - {name} -- Discord name of the member excluding their Discord discriminator.
        - {username} -- Discord name of the member including their Discord discriminator.
        - {discriminator} -- Discriminator of the member.

    """

    @staticmethod
    async def send_welcome_message(guild_profile, member):
        if guild_profile.welcome_message and not guild_profile.welcome_banner_enabled:
            await guild_profile.welcome_message_channel.send(
                guild_profile.welcome_message.format(**MessageTemplateMember(member).__dict__))

    @staticmethod
    async def send_direct_welcome_message(guild_profile, member):
        if guild_profile.direct_welcome_message:
            try:
                await member.send(guild_profile.direct_welcome_message.format(**MessageTemplateMember(member).__dict__))
            except discord.Forbidden:
                pass

    @WelcomeBase.listener(name="on_member_join")
    async def on_member_join_message(self, member):
        guild_profile = await self.cache.get_profile(member.guild.id)
        # Always send direct message regardless of member is verified or not.
        await self.send_direct_welcome_message(guild_profile, member)
        # Send welcome message only when User Verification is disabled.
        if not guild_profile.verification.role:
            await self.send_welcome_message(guild_profile, member)

    @WelcomeBase.listener(name="on_member_verification")
    async def on_member_verification_message(self, guild_profile, member):
        await self.send_welcome_message(guild_profile, member)

    @WelcomeBase.welcome.group(name="message", aliases=["msg"], invoke_without_command=True)
    async def welcome_message(self, ctx):
        """Displays the template being used for Welcome Messages if it has been set already.

        If Welcome Banner is enabled, the Welcome Messages are included along with the welcome banners.
        If User Verification is enabled, welcome message is sent only after the member is verified.

        """
        if not ctx.guild_profile.welcome_message:
            return await ctx.send_line(f"❌    Welcome Message has not been set in the server.")
        embed = ctx.embed_line("Welcome Message Template", ctx.guild.icon_url)
        embed.description = f"```css\n{ctx.guild_profile.welcome_message}```"
        await ctx.send(embed=embed)

    @welcome_message.command(name="set")
    async def set_welcome_message(self, ctx, channel: typing.Optional[discord.TextChannel], *, message: Template):
        """Setup and enable Welcome Messages using provided template. The Welcome Messages are sent to the current or
        any specified channel whenever a new user joins the server.

        """
        channel = channel or ctx.channel
        await ctx.guild_profile.set_welcome_message(message, channel)
        await ctx.send_line(f"✅    Welcome messages has been set in #{channel} channel.")

    @welcome_message.command(name="remove", aliases=["delete"])
    async def remove_welcome_message(self, ctx):
        """Remove and disable Welcome Messages from the server."""
        if not await ctx.confirm():
            return
        await ctx.guild_profile.remove_welcome_message()
        await ctx.send_line(f"✅    Welcome messages has been disabled and removed.")

    @WelcomeBase.welcome.group(name="directmessage", aliases=["dm", "directmsg"], invoke_without_command=True)
    async def direct_message(self, ctx):
        """Displays the template being using for Direct Welcome Messages if it has been set already.

        Direct welcome messages are sent just after user joins the server irrespective of User Verification.

        """
        if not ctx.guild_profile.direct_welcome_message:
            return await ctx.send_line(f"❌    Direct Welcome Messages has not been set in the server.")
        embed = ctx.embed_line("Direct Welcome Message Template", ctx.guild.icon_url)
        embed.description = f"```css\n{ctx.guild_profile.direct_welcome_message}```"
        await ctx.send(embed=embed)

    @direct_message.command(name="set")
    async def set_direct_welcome_message(self, ctx, *, message: Template):
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
