import discord
from discord.ext import commands
import os
from .utils.paginators import SimplePaginator, HelpPaginator
import inspect
import traceback
import subprocess
from cogs.utils.util import get_reaction_yes_no, get_random_embed_color

from cogs.utils.rmenu import Menu
import git

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
        print("Restarting bot.")
        await self.bot.logout()
        os.system("systemctl restart cosmos.service")
        os._exit(0)

    @commands.command(hidden=True)
    async def quit(self, ctx, ):
        "Shut Downs the bot"
        await ctx.send("Logging out and stopping `cosmos.service`.")
        await self.bot.logout()
        os.system("systemctl stop cosmos.service")
        os._exit(0)

    @commands.command(rest_is_raw=True, hidden=True, aliases=["say", "vomit"])
    async def echo(self, ctx, *, content):
        await ctx.message.delete()
        await ctx.send(content)

    @commands.group(hidden=True)
    async def update(self, ctx):
        """Command which pulls new update from repository and restarts `cosmos.service`."""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(color=get_random_embed_color())
            m1 = await ctx.send("Pulling up new updates.")
            process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
            output = process.communicate()[0]
            await m1.add_reaction(get_reaction_yes_no()["yes"])
            new_repo = git.Repo(os.getcwd()).head.reference
            embed.set_author(name="Update info", icon_url=ctx.author.avatar_url)
            embed.description = "Updating to commit `"+new_repo.commit.hexsha+"`."
            embed.add_field(name="Description", value=new_repo.commit.message)
            embed.add_field(name="Changed files", value=new_repo.commit.stats.files)
            await ctx.send(embed=embed)
            m2 = await ctx.send("Logging out and restarting `cosmos.service`.")
            await self.bot.logout()
            os.system("systemctl restart cosmos.service")
            os._exit(0)

    @update.command(name="soft")
    async def update_soft(self, ctx):
        """Updates the files without restarting `cosmos.service`."""
        embed = discord.Embed(color=get_random_embed_color())
        old_repo = git.Repo(os.getcwd()).head.reference
        m1 = await ctx.send("Pulling up new updates and making soft update.")
        process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
        output = process.communicate()[0]
        await m1.add_reaction(get_reaction_yes_no()["yes"])
        new_repo = git.Repo(os.getcwd()).head.reference
        embed.set_author(name="Update info", icon_url=ctx.author.avatar_url)
        embed.description = "Updating to commit `"+new_repo.commit.hexsha+"`."
        embed.add_field(name="Description", value=new_repo.commit.message)
        embed.add_field(name="Changed files", value=new_repo.commit.stats.files)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Admin(bot))
