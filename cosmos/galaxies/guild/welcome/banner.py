from io import BytesIO

import discord
import typing

from cosmos import exceptions
from .base import WelcomeBase, MessageTemplateMember


class WelcomeBanner(WelcomeBase):
    """A plugin to serve and manage customized static or animated GIF Welcome Banners.

    Welcome Banner is PNG or GIF image file which is generated and sent when any member joins the server.
    It can be customized by adding a custom text message which is written over it. Moreover the border color can
    be customized by setting a new theme color from Theme Settings.

    If User Verification is enabled, welcome banners are sent only after the member is verified.

    """

    async def send_welcome_banner(self, guild, member, channel: discord.TextChannel = None):
        banner_format = guild.welcome_banner_url.split(".")[-1]
        if banner_format.lower() == "gif" and not guild.is_prime:
            raise exceptions.GuildNotPrime
        channel = channel or guild.welcome_banner_channel
        options = dict()
        if guild.theme.color:
            options["border_color"] = options["font_color"] = options["avatar_border_color"] = str(guild.theme.color)
        banner_bytes = await self.bot.image_processor.discord.get_welcome_banner(
            guild.welcome_banner_url, str(member.avatar_url), member.name, guild.welcome_banner_text, **options)
        file = discord.File(BytesIO(banner_bytes), filename=f"{guild.plugin.data.settings.banner_name}.{banner_format}")
        if guild.welcome_message:
            await channel.send(guild.welcome_message.format(**MessageTemplateMember(member).__dict__), file=file)
        else:
            await channel.send(file=file)

    @WelcomeBase.listener(name="on_member_join")
    async def on_member_join_banner(self, member):
        guild_profile = await self.cache.get_profile(member.guild.id)
        if not guild_profile.verification.role:
            if guild_profile.welcome_banner_enabled:
                try:
                    await self.send_welcome_banner(guild_profile, member)
                except exceptions.GuildNotPrime:
                    pass

    @WelcomeBase.listener(name="on_member_verification")
    async def on_member_verification_banner(self, guild_profile, member):
        if guild_profile.welcome_banner_enabled:
            try:
                await self.send_welcome_banner(guild_profile, member)
            except exceptions.GuildNotPrime:
                pass

    @WelcomeBase.cooldown(1, 5, WelcomeBase.bucket_type.guild)
    @WelcomeBase.welcome.group(name="banner", invoke_without_command=True)
    async def welcome_banner(self, ctx):
        """Displays previously configured welcome banner."""
        if not ctx.guild_profile.welcome_banner_url:
            return await ctx.send_line("❌    Please configure welcome banner settings.")
        await self.send_welcome_banner(ctx.guild_profile, ctx.author, ctx.channel)

    @welcome_banner.error
    async def welcome_banner_error(self, ctx, error):
        if isinstance(error, exceptions.GuildNotPrime):
            return await ctx.send_line(f"❌    Get prime to use GIF banners or set static banner.")

    @WelcomeBase.cooldown(1, 3, WelcomeBase.bucket_type.guild)
    @welcome_banner.command(name="set")
    async def set_welcome_banner(self, ctx, banner_url, channel: typing.Optional[discord.TextChannel] = None, *, text):
        """Configure and set server welcome banner.
        You should specify direct URL of the banner template which can be either JPEG or PNG. Prime servers can use
        GIF banner templates. It uses current channel to send welcome banners or any other if specified with custom
        required text.

        """
        channel = channel or ctx.channel
        banner_format = banner_url.split(".")[-1]
        if banner_format not in self.plugin.data.settings.banner_formats:
            return await ctx.send_line("❌    Please use supported image format.")
        if banner_format == "gif" and not ctx.guild_profile.is_prime:
            return await ctx.send_line("❌    Sorry but only prime servers can use GIF banners.")
        banner_size = round((await self.bot.image_processor.utils.fetch_size(banner_url)) / 1048576, 2)
        banner_max_size = self.plugin.data.settings.banner_max_size
        if banner_size > banner_max_size:
            return await ctx.send_line(f"❌    Banner should be less than {banner_max_size} MB in size however size of "
                                       f"provided banner seems to be of {banner_size} MB.")
        await ctx.guild_profile.set_welcome_banner(banner_url, text, channel.id)
        # TODO: Actually try generating test welcome banner.
        await ctx.send_line(f"Welcome banners set for {ctx.guild.name}.", ctx.guild.icon_url)

    @welcome_banner.command(name="enable")
    async def enable_welcome_banner(self, ctx):
        """Enable sending welcome banners in channel."""
        if not ctx.guild_profile.welcome_banner_url:
            return await ctx.send_line("❌    Please configure welcome banner settings.")
        if ctx.guild_profile.welcome_banner_enabled:
            return await ctx.send_line(f"❌    Welcome banners are already enabled in {ctx.guild.name}.")
        await ctx.guild_profile.enable_welcome_banner()
        await ctx.send_line(f"Enabled welcome banners for {ctx.guild.name}.", ctx.guild.icon_url)

    @welcome_banner.command(name="disable")
    async def disable_welcome_banner(self, ctx):
        """Disable sending welcome banner in channel."""
        if not ctx.guild_profile.welcome_banner_url:
            return await ctx.send_line("❌    Please configure welcome banner settings.")
        if not ctx.guild_profile.welcome_banner_enabled:
            return await ctx.send_line(f"❌    Welcome banners are already disabled in {ctx.guild.name}.")
        await ctx.guild_profile.enable_welcome_banner(enable=False)
        await ctx.send_line(f"Disabled welcome banners for {ctx.guild.name}.", ctx.guild.icon_url)
