import io
import textwrap
import traceback
from abc import ABC
from contextlib import redirect_stdout
from pprint import pformat

import discord
from discord.ext import commands

from ....functions import Cog


class Evaluator(Cog, ABC):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self._last_result = None

    async def __local_check(self, ctx):
        return await self.bot.is_owner(ctx.author)

    @staticmethod
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    # noinspection PyBroadException
    @commands.command(hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        async with ctx.loading():
            try:
                exec(to_compile, env)
            except Exception as e:
                return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

            func = env['func']
            try:
                with redirect_stdout(stdout):
                    ret = await func()
            except Exception as e:
                value = stdout.getvalue()
                await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
            else:
                value = stdout.getvalue()
                try:
                    await ctx.message.add_reaction('\u2705')
                except:
                    pass

                if ret is None:
                    if value:
                        try:
                            await ctx.send(f'```py\n{value}\n```')
                        except discord.HTTPException:
                            haste_url = await self.bot.utilities.haste(pformat(value))
                            await ctx.send(haste_url.py)
                else:
                    self._last_result = ret
                    try:
                        await ctx.send(f'```py\n{value}{ret}\n```')
                    except discord.HTTPException:
                        haste_url = await self.bot.utilities.haste(pformat(f"{value}{ret}"))
                        await ctx.send(haste_url.py)
