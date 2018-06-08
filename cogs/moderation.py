import discord
from discord.ext import commands

from cogs.utils.util import get_reaction_yes_no

class Moderation(object):

    def __init__(self, bot):
        self.bot = bot
        self.soft_muted = {}

    async def on_message(self, message):
        if message.guild.id in self.soft_muted and message.author.id in self.soft_muted[message.guild.id]:
            await message.delete()

    @commands.group(hidden=True)
    @commands.has_permissions(administrator=True)
    async def mute(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("No sub-command called.")

    @mute.command(name="soft")
    async def mute_soft(self, ctx, member:discord.Member):
        """Soft mutes a member - deletes each and every message sent by member."""
        await ctx.message.add_reaction(get_reaction_yes_no()["yes"])
        if ctx.guild.id not in self.soft_muted:
            self.soft_muted[ctx.guild.id] = []
        self.soft_muted[ctx.guild.id].append(member.id)

    @commands.group(hidden=True)
    @commands.has_permissions(administrator=True)
    async def unmute(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("No sub-command called.")

    @unmute.command(name="soft")
    async def unmute_soft(self, ctx, member:discord.Member):
        """Unmute soft muted member."""
        self.soft_muted[ctx.guild.id].remove(member.id)
        await ctx.message.add_reaction(get_reaction_yes_no()["yes"])

def setup(bot):
    bot.add_cog(Moderation(bot))
