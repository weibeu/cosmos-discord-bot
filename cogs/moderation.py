import discord
from discord.ext import commands

from cogs.utils.util import get_reaction_yes_no
from cogs.utils import checks

class Moderation(object):

    def __init__(self, bot):
        self.bot = bot
        self.soft_muted = {}

    async def on_message(self, message):
        try:
            if message.guild.id in self.soft_muted and message.author.id in self.soft_muted[message.guild.id]:
                await message.delete()
        except:
            pass

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

    @commands.command(name="massmove", aliases=["move"])
    @checks.admin_or_permissions(move_members=True)
    async def mass_move(self, ctx, from_channel: discord.VoiceChannel, to_channel: discord.VoiceChannel):
        """Move all members in specified voice channel to another.
        Requires Admins or move member permissions."""
        try:
            voice_list = list(from_channel.members)
            for member in voice_list:
                await member.move_to(to_channel)
        except discord.Forbidden:
            await ctx.send('I have no permission to move members.')
        except discord.HTTPException:
            await ctx.send('A error occured. Please try again')
        await ctx.message.add_reaction(get_reaction_yes_no()["yes"])

def setup(bot):
    bot.add_cog(Moderation(bot))

























