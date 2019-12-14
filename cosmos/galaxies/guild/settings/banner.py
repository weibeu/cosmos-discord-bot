import discord
import typing

from .base import Settings


class BannerSettings(Settings):

    @Settings.listener()
    async def on_member_join(self, member):
        guild_profile = await self.cache.get_profile(member.guild.id)
        if guild_profile.welcome_banner_enabled:
            await guild_profile.send_welcome_banner(member.name, str(member.avatar_url))

    @Settings.group(name="welcome", aliases=["join"])
    async def welcome(self, ctx):
        pass

    @welcome.group(name="banner", invoke_without_command=True)
    async def welcome_banner(self, ctx):
        if not ctx.guild_profile.welcome_banner_url:
            return await ctx.send_line("❌    Please configure welcome banner settings.")
        await ctx.guild_profile.send_welcome_banner(ctx.author.name, str(ctx.author.avatar_url), ctx.channel)

    @welcome_banner.command(name="set")
    async def set_welcome_banner(self, ctx, banner_url, channel: typing.Optional[discord.TextChannel] = None, *, text):
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
        if not ctx.guild_profile.welcome_banner_url:
            return await ctx.send_line("❌    Please configure welcome banner settings.")
        if ctx.guild_profile.welcome_banner_enabled:
            return await ctx.send_line(f"❌    Welcome banners are already enabled in {ctx.guild.name}.")
        await ctx.guild_profile.enable_welcome_banner()
        await ctx.send_line(f"Enabled welcome banners for {ctx.guild.name}.", ctx.guild.icon_url)

    @welcome_banner.command(name="disable")
    async def disable_welcome_banner(self, ctx):
        if not ctx.guild_profile.welcome_banner_url:
            return await ctx.send_line("❌    Please configure welcome banner settings.")
        if not ctx.guild_profile.welcome_banner_enabled:
            return await ctx.send_line(f"❌    Welcome banners are already disabled in {ctx.guild.name}.")
        await ctx.guild_profile.enable_welcome_banner(enable=False)
        await ctx.send_line(f"Disabled welcome banners for {ctx.guild.name}.", ctx.guild.icon_url)
