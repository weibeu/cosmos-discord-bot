import discord
from discord.ext import commands
import os
from .utils.paginators import SimplePaginator, HelpPaginator
import inspect
import traceback
import git

from cogs.utils.rmenu import Menu

class Admin(object):

    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return ctx.author.id in [331793750273687553]

    @commands.command(hidden=True)
    async def cog(self, ctx, arg, *cogs):
        """`cog <load/l> <cogs separated by comma>` : loads specified cogs from /cogs directory.
        `cog <unload/u> <cogs separated by comma>` : unloads specified cogs from bot."""
        if arg.lower() in ['load', 'l']:
            for cog in cogs:
                if "cogs."+cog in self.bot.cog_list:
                    try:
                        self.bot.load_extension("cogs.{0}".format(cog))
                        await ctx.send("cog `{0}` loaded successfully".format(cog))
                        print("cog '{0}' loaded successfully".format(cog))
                    except Exception as e:
                        self.bot.sentry_client.captureException()
                        await ctx.send("cog `{0}` load failed".format(cog))
                        print("cog '{0}' load failed".format(cog))
                else:
                    await ctx.send("No cog named `{0}` found in /cogs".format(cog))
        elif arg.lower() in ['unload', 'u']:
            for cog in cogs:
                if "cogs."+cog in self.bot.cog_list:
                    try:
                        self.bot.unload_extension("cogs.{0}".format(cog))
                        await ctx.send("cog `{0}` unloaded".format(cog))
                        print("cog '{0}' unloaded".format(cog))
                    except Exception as e:
                        self.bot.sentry_client.captureException()
                        await ctx.send("cog `{0}` unload failed".format(cog))
                        print("cog '{0}' unload failed".format(cog))
                else:
                    await ctx.send("No cog named `{0}` found in /cogs".format(cog))
        else:
            await ctx.send("unknown argument provided.")

    @commands.command(hidden=True)
    async def cog_reload(self, ctx):
        for c in self.bot.cog_list:
            try:
                self.bot.unload_extension(c)
                self.bot.load_extension(c)
                print("cog '{0}' reloaded successfully".format(c))
                await ctx.send("cog `{0}` reloaded successfully".format(c))
            except Exception as e:
                self.bot.sentry_client.captureException()
                print("cog '{0}' reload failed".format(c))
                await ctx.send("cog `{0}` reload failed".format(c))

    @commands.command(hidden=True)
    async def restart(self, ctx):
        """Logouts using bot.logout(), executes loop.py and restarts the bot"""
        await ctx.send("Restarting.....")
        print("Restarting bot...")
        await ctx.bot.shutdown(restart=True)

    @commands.command(hidden=True)
    async def quit(self, ctx, ):
        "Shut Downs the bot"
        await ctx.send("Bot shutdown.....")
        await self.bot.logout()
        os._exit(0)

    @commands.command(rest_is_raw=True, hidden=True, aliases=["say", "vomit"])
    async def echo(self, ctx, *, content):
        await ctx.message.delete()
        await ctx.send(content)

    


def setup(bot):
    bot.add_cog(Admin(bot))
