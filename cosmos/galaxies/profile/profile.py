from discord.ext import commands

from .. import Cog
from .models import ProfileCache


class Profile(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.cache = ProfileCache(self.plugin)
        self.bot.loop.create_task(self.cache.prepare())

    @commands.command()
    async def profile(self, ctx):
        profile = await self.cache.get_profile(ctx.author.id)
        if profile:
            embed = self.bot.theme.embeds.primary(title="Profile")
            embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
            embed.add_field(name="Reputation points", value=str(profile.reps))
            embed.add_field(name="Experience points", value=str(profile.xp))
            if profile.description:
                embed.add_field(name="Profile description", value=profile.description)
            await ctx.send(embed=embed)
        else:
            async with ctx.loading():
                await ctx.send(embed=self.bot.theme.embeds.one_line.primary("Welcome! Creating your Cosmos profile."))
                profile = await self.cache.create_profile(ctx.author.id)
                embed = self.bot.theme.embeds.primary(title="Profile")
                embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar_url)
                embed.add_field(name="Reputation points", value=str(profile.reps))
                embed.add_field(name="Experience points", value=str(profile.xp))
                if profile.description:
                    embed.add_field(name="Profile description", value=profile.description)
                await ctx.send(embed=embed)
