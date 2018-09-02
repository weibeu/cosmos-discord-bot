import discord
import subprocess
import os
import git

from discord.ext import commands
from cogs.utils.util import get_reaction_yes_no, get_random_embed_color
from cogs.utils import db

class Admin(object):

    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return ctx.author.id in [331793750273687553, 250900865446182922]

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
        await ctx.send("Forcing pending jobs to complete.")
        #force complete pending jobs
        #   removing on member join cooldown role if any has
        omjcd_settings = await db.get_omjcd_settings(self.bot.guilds)
        for guild_id in omjcd_settings:
            guild  = discord.utils.get(self.bot.guilds, id=int(guild_id))
            role = discord.utils.get(guild.roles, id=int(omjcd_settings[guild_id]["role"]))
            for member in role.members:
                try:
                    await member.remove_roles(role, reason="Removed cooldown role.")
                except:
                    pass
        await ctx.send("All jobs completed.")
        await ctx.send("Restarting.....")
        print("Restarting bot.")
        await self.bot.logout()
        os.system("systemctl restart cosmos.service")
        os._exit(0)

    @commands.command(hidden=True)
    async def quit(self, ctx, ):
        "Shut Downs the bot"
        await ctx.send("Forcing pending jobs to complete.")
        #force complete pending jobs
        #   removing on member join cooldown role if any has
        omjcd_settings = await db.get_omjcd_settings(self.bot.guilds)
        for guild_id in omjcd_settings:
            guild  = discord.utils.get(self.bot.guilds, id=int(guild_id))
            role = discord.utils.get(guild.roles, id=int(omjcd_settings[guild_id]["role"]))
            for member in role.members:
                try:
                    await member.remove_roles(role, reason="Removed cooldown role.")
                except:
                    pass
        await ctx.send("All jobs completed.")
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
            process = subprocess.Popen(['git', 'reset', '--hard', 'HEAD^'], stdout=subprocess.PIPE)
            output = process.communicate()[0]
            process = subprocess.Popen(["git", "clean", "-fd"], stdout=subprocess.PIPE)
            output += process.communicate()[0]
            process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
            output += process.communicate()[0]
            await ctx.send(embed=discord.Embed(description=f"```css\n{output}```\n", colour=get_random_embed_color()))
            await m1.add_reaction(get_reaction_yes_no()["yes"])
            new_repo = git.Repo(os.getcwd()).head.reference
            embed.set_author(name="Update info", icon_url=ctx.author.avatar_url)
            embed.description = "Updating to commit `"+new_repo.commit.hexsha+"`.\n**Description:**\t`"+new_repo.commit.message+"`."
            for file in new_repo.commit.stats.files:
                try:
                    embed.add_field(name=file, value="`Insertions:`\t"+str(new_repo.commit.stats.files[file]['insertions'])+"\n`Deletions:`\t"+str(new_repo.commit.stats.files[file]['deletions'])+"\n`Lines:`\t"+str(new_repo.commit.stats.files[file]["lines"]))
                except:
                    pass
            try:
                await ctx.send(embed=embed)
            except:
                pass
            await ctx.send("Forcing pending jobs to complete.")
            #   force complete pending jobs
            #   removing on member join cooldown role if any has
            omjcd_settings = await db.get_omjcd_settings(self.bot.guilds)
            for guild_id in omjcd_settings:
                guild = discord.utils.get(self.bot.guilds, id=int(guild_id))
                role = discord.utils.get(guild.roles, id=int(
                    omjcd_settings[guild_id]["role"]))
                for member in role.members:
                    try:
                        await member.remove_roles(role, reason="Removed cooldown role.")
                    except:
                        pass
            await ctx.send("All jobs completed.")
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
        process = subprocess.Popen(['git', 'reset', '--hard', 'HEAD^'], stdout=subprocess.PIPE)
        output = process.communicate()[0]
        process = subprocess.Popen(["git", "clean", "-fd"], stdout=subprocess.PIPE)
        output += process.communicate()[0]
        process = subprocess.Popen(["git", "pull"], stdout=subprocess.PIPE)
        output += process.communicate()[0]
        await ctx.send(embed=discord.Embed(description=f"```css\n{output}```\n", colour=get_random_embed_color()))
        await m1.add_reaction(get_reaction_yes_no()["yes"])
        new_repo = git.Repo(os.getcwd()).head.reference
        embed.set_author(name="Update info", icon_url=ctx.author.avatar_url)
        embed.description = "Updating to commit `"+new_repo.commit.hexsha+"`.\n**Description:**\t`"+new_repo.commit.message+"`."
        for file in new_repo.commit.stats.files:
            try:
                embed.add_field(name=file, value="`Insertions:`\t"+str(new_repo.commit.stats.files[file]['insertions'])+"\n`Deletions:`\t"+str(new_repo.commit.stats.files[file]['deletions'])+"\n`Lines:`\t"+str(new_repo.commit.stats.files[file]["lines"]))
            except:
                pass
        try:
            await ctx.send(embed=embed)
        except:
            pass

def setup(bot):
    bot.add_cog(Admin(bot))
