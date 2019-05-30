from discord.ext.commands import has_permissions

import discord

from .base import Settings


class ThemeSettings(Settings):

    @Settings.group(name="theme", aliases=["themes"])
    @has_permissions(manage_guild=True)
    async def theme_setting(self, ctx):
        pass

    @theme_setting.command(name="color", aliases=["colour"])
    async def theme_color(self, ctx, color: discord.Color = None):
        if not color:
            if ctx.guild_profile.theme.color:
                res = f"{ctx.guild.name} theme color is set to {ctx.guild_profile.theme.color}."
            else:
                res = f"{ctx.guild.name} theme color isn't set yet."
            return await ctx.send_line(res, ctx.guild.icon_url)

        await ctx.guild_profile.theme.set_color(color.value)
        await ctx.send_line(
            f"{ctx.guild.name} theme color has been set to {ctx.guild_profile.theme.color}.", ctx.guild.icon_url
        )
