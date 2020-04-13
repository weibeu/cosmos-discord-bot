from contextlib import redirect_stdout

import io
import time
import discord
import textwrap
import traceback

from ..base import Admin
from datetime import datetime


# noinspection PyBroadException
class Evaluator(Admin):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_result = None

    @staticmethod
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @Admin.command(name='eval', aliases=["py", "evaluate"])
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        try:
            guild_profile = await self.bot.guild_cache.get_profile(ctx.guild.id)
        except AttributeError:
            guild_profile = None

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
                start_eval_at = time.time()
                exec(to_compile, env)
            except Exception as e:
                embed = ctx.embed_line(f"❗    Error while compiling.")
                embed.description = f'```py\n{e.__class__.__name__}: {e}\n```'
                embed.timestamp = datetime.now()
                return await ctx.send(embed=embed)

            func = env['func']
            try:
                with redirect_stdout(stdout):
                    ret = await func()
                    evaluated_in = time.time() - start_eval_at
            except Exception as _:
                value = stdout.getvalue()
                embed = ctx.embed_line(f"⚠    An unexpected exception occurred.")
                embed.description = f'```py\n{value}{traceback.format_exc()}\n```'
                embed.timestamp = datetime.now()
                await ctx.send(embed=embed)
            else:
                value = stdout.getvalue()

                self._last_result = ret

                try:
                    embed = ctx.embed_line(f"✅    Evaluated in {round(evaluated_in, 3)} seconds.")
                    embed.description = f"```py\n{body}\n```"
                    if value:
                        embed.add_field(name="Standard Output", value=f'```py\n{value}\n```')
                    if ret:
                        embed.add_field(name="Returned", value=f'```py\n{ret}\n```')
                    embed.timestamp = datetime.now()
                    await ctx.send(embed=embed)
                except discord.HTTPException:
                    haste_url = await self.bot.utilities.haste(f"{value}{ret}")
                    await ctx.send_line(f"🔗    {haste_url.py}")
