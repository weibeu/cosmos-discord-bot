import discord
from discord.ext import commands
import datetime
import time

from cogs.utils import db
from cogs.utils.config import get_config_value
from cogs.utils.dataIO import dataIO
from cogs.utils.checks import embed_perms, cmd_prefix_len, parse_prefix, get_user
from cogs.utils.util import get_random_embed_color
from .utils.paginator import HelpPaginator, CannotPaginate
import psutil

class Core(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Calculates the ping time."""
        # [p]ping

        t_1 = time.perf_counter()
        await ctx.trigger_typing()  # tell Discord that the bot is "typing", which is a very simple request
        t_2 = time.perf_counter()
        time_delta = round((t_2-t_1)*1000)  # calculate the time needed to trigger typing
        await ctx.send("Pong! | ` {0} ms `".format(time_delta))  # send a message telling the user the calculated ping time

    @commands.group(aliases=['status'], pass_context=True)
    async def stats(self, ctx):
        """Bot stats."""
        uptime = (datetime.datetime.now() - self.bot.uptime)
        hours, rem = divmod(int(uptime.total_seconds()), 3600)
        minutes, seconds = divmod(rem, 60)
        days, hours = divmod(hours, 24)
        if days:
            time = '%s days, %s hours, %s minutes, and %s seconds' % (days, hours, minutes, seconds)
        else:
            time = '%s hours, %s minutes, and %s seconds' % (hours, minutes, seconds)
        game = self.bot.game
        if not game:
            game = 'None'
        channel_count = 0
        for guild in self.bot.guilds:
            channel_count += len(guild.channels)
        if not self.bot.command_count:
            most_used_cmd = 'Not enough info'
        else:
            cmd_name = max(self.bot.command_count, key=self.bot.command_count.get)
            total_usage = self.bot.command_count[str(cmd_name)]
            plural = '' if total_usage == 1 else 's'
            most_used_cmd = '{} - {} use{}'.format(cmd_name, total_usage, plural)
        if embed_perms(ctx.message):
            em = discord.Embed(title='Bot Stats', color=get_random_embed_color())
            em.add_field(name=u'\U0001F553 Uptime', value=time, inline=False)
            em.add_field(name=u'\u2328 Most Used Cmd', value=most_used_cmd)
            em.add_field(name='🔺 discord.py version', value=discord.__version__, inline=False)
            em.add_field(name=u'\u2694 Servers', value=str(len(self.bot.guilds)))
            em.add_field(name=u'\ud83d\udcd1 Channels', value=str(channel_count))
            g = u'\U0001F3AE Game'
            if '=' in game: g = '\ud83c\udfa5 Stream'
            em.add_field(name=g, value=game)
            em.add_field(name="⚙ Logical CPUs Cores", value=str(psutil.cpu_count()))
            try:
                mem_usage = '{:.2f} MiB'.format(__import__('psutil').Process().memory_full_info().uss / 1024 ** 2)
            except AttributeError:
                # OS doesn't support retrieval of USS (probably BSD or Solaris)
                mem_usage = '{:.2f} MiB'.format(__import__('psutil').Process().memory_full_info().rss / 1024 ** 2)
            em.add_field(name=u'\U0001F4BE Memory usage:', value=str(mem_usage)+" / "+str(round(psutil.virtual_memory().used/1024**2, 3))+" MiB")
            em.add_field(name='📈 CPU usage', value=str(psutil.cpu_percent())+" %")
            await ctx.send(content=None, embed=em)
        else:
            msg = '**Bot Stats:** ```Uptime: %s\nguilds: %s\nGame: %s```' % (
            time, str(len(self.bot.guilds)), game)
            await ctx.send(msg)
        await ctx.message.delete()

    @commands.command(name='help')
    async def _help(self, ctx, *, command: str = None):
        """Shows help about a command or the bot"""

        try:
            if command is None:
                p = await HelpPaginator.from_bot(ctx)
            else:
                entity = self.bot.get_cog(command) or self.bot.get_command(command)

                if entity is None:
                    clean = command.replace('@', '@\u200b')
                    return await ctx.send(f'Command or category "{clean}" not found.')
                elif isinstance(entity, commands.Command):
                    p = await HelpPaginator.from_command(ctx, entity)
                else:
                    p = await HelpPaginator.from_cog(ctx, entity)

            await p.paginate()
        except Exception as e:
            await ctx.send(e)

    @commands.command(aliases=['invite'])
    @commands.is_owner()
    async def auth(self, ctx):
        """Bot's auth URL to join server."""
        perms = discord.Permissions.none()
        perms.administrator = True
        e = discord.Embed()
        e.title = "Invite Link - Bot Cosmos"
        e.description = f'<{discord.utils.oauth_url(self.bot.client_id, perms)}>'
        e.colour = get_random_embed_color()
        await ctx.send(embed=e)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        await db.add_settings(guild.id)

def setup(bot):
    bot.add_cog(Core(bot))
