import discord
from discord.ext import commands

import traceback
import datetime
import logging
from configparser import ConfigParser

# Lame
log = logging.getLogger('myst')


class MystException(Exception):
    """Base exception class for Myst"""
    pass


class DownloadError(commands.CommandError):
    def __init__(self, msg):
        super().__init__(message=msg)


class PlayerGarbageError(discord.DiscordException):
    def __init__(self, etype, error, guild):
        msg = f'PLAYERGARBAGE:: CancelTask: {etype} - {error} in [{guild}:::{guild.id}]'
        log.error(msg)
        super().__init__(msg)


class ErrorHandler:

    def __init__(self, bot):
        self.bot = bot
        self.wh_info = ConfigParser()
        self.wh_info.read('/home/myst/mystbot/mystconfig.ini')  # !!!VPS!!!

    @property
    def webhook(self):
        wh_id = self.wh_info.get('WH', '_id')
        wh_token = self.wh_info.get('WH', '_key')
        hook = discord.Webhook.partial(id=wh_id, token=wh_token, adapter=discord.AsyncWebhookAdapter(self.bot.session))
        return hook

    async def on_command_error(self, ctx, error):
        """The event triggered when an error is raised while invoking a command.
        ctx   : Context
        error : Exception"""

        if isinstance(error, commands.CheckFailure):
            if ctx.author.id == self.bot.appinfo.owner.id:
                return await ctx.reinvoke()

        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError, commands.DisabledCommand, commands.CheckFailure,
                   commands.CommandOnCooldown)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except:
                pass

        exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=False))

        e = discord.Embed(title='Command Error', colour=0xF31431)
        e.add_field(name='Name', value=ctx.command.qualified_name)
        e.add_field(name='Author', value=f'{ctx.author} (ID: {ctx.author.id})')

        fmt = f'Channel: {ctx.channel} (ID: {ctx.channel.id})'
        if ctx.guild:
            fmt = f'{fmt}\nGuild: {ctx.guild} (ID: {ctx.guild.id})'

        e.add_field(name='Location', value=fmt, inline=False)

        if len(exc) > 2024:
            gist = await self.bot.create_gist(f'Command Error: {ctx.command.qualified_name}', [('error.py', exc)])
            e.description = gist
        else:
            e.description = f'```py\n{exc}\n```'

        e.timestamp = datetime.datetime.utcnow()
        await self.webhook.send(embed=e)


class BotChecks:

    def __init__(self, bot):
        self.bot = bot
        self.bot.add_check(self.check_botblocks)

    async def check_botblocks(self, ctx):

        if ctx.author.id in self.bot.blocks:
            return False
        return True


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
    bot.add_cog(BotChecks(bot))
