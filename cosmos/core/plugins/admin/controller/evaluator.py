import io
import textwrap
import traceback
from contextlib import redirect_stdout
from pprint import pformat

import discord

from ....functions import Cog


# noinspection PyBroadException
class Evaluator(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self._last_result = None

    async def cog_check(self, ctx):    # ! Never ever remove this method.
        await super().cog_check(ctx)
        return await self.bot.is_owner(ctx.author)

    @staticmethod
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @Cog.command(name='eval', aliases=["py", "evaluate"])
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        guild_profile = await self.bot.guild_cache.get_profile(ctx.guild.id)

        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'guild_profile': guild_profile,
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
            except Exception as _:
                value = stdout.getvalue()
                await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
            else:
                await ctx.message.add_reaction('\u2705')

                value = stdout.getvalue()

                if ret is None:
                    if value:
                        try:
                            await ctx.send(f'```py\n{value}\n```')
                        except discord.HTTPException:
                            haste_url = await self.bot.utilities.haste(pformat(value, indent=4))
                            await ctx.send(haste_url.py)
                else:
                    self._last_result = ret
                    try:
                        await ctx.send(f'```py\n{value}{ret}\n```')
                    except discord.HTTPException:
                        haste_url = await self.bot.utilities.haste(pformat(f"{value}{ret}", indent=4))
                        await ctx.send(haste_url.py)
