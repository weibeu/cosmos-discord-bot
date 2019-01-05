import discord
from discord.ext import commands
import asyncio

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
    async def mute(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("No sub-command called.")

    @commands.group(hidden=True)
    async def unmute(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("No sub-command called.")

    @mute.command(name="soft")
    @commands.has_permissions(administrator=True)
    async def mute_soft(self, ctx, member:discord.Member):
        """Soft mutes a member - deletes each and every message sent by member."""
        await ctx.message.add_reaction(get_reaction_yes_no()["yes"])
        if ctx.guild.id not in self.soft_muted:
            self.soft_muted[ctx.guild.id] = []
        self.soft_muted[ctx.guild.id].append(member.id)

    @unmute.command(name="soft")
    @commands.has_permissions(administrator=True)
    async def unmute_soft(self, ctx, member:discord.Member):
        """Unmute soft muted member."""
        self.soft_muted[ctx.guild.id].remove(member.id)
        await ctx.message.add_reaction(get_reaction_yes_no()["yes"])

    @mute.command(name="voice")
    @checks.admin_or_permissions(mute_members=True)
    async def mute_voice(self, ctx, channel: discord.VoiceChannel = None):
        """Mutes all member present in current or specified Voice Channel except you."""
        if channel is None:
            try:
                channel = ctx.author.voice.channel
            except:
                await ctx.send("You're not in Voice Channel at the moment. Please specify channel to mute members.")
        try:
            members = list(channel.members)
            for member in members:
                try:
                    if member.id != ctx.author.id:
                        await member.edit(mute=True)
                except:
                    pass
            await ctx.message.add_reaction(get_reaction_yes_no()["yes"])
            await asyncio.sleep(2.7)
            await ctx.message.delete()
        except:
            await ctx.send("Something went wrong muting members.")

    @unmute.command(name="voice")
    @checks.admin_or_permissions(mute_members=True)
    async def unmute_voice(self, ctx, channel: discord.VoiceChannel = None):
        """Unmutes all member present in current or specified Voice Channel."""
        if channel is None:
            try:
                channel = ctx.author.voice.channel
            except:
                await ctx.send("You're not in Voice Channel at the moment. Please specify channel to mute members.")
        try:
            members = list(channel.members)
            for member in members:
                try:
                    if member.id != ctx.author.id:
                        await member.edit(mute=False)
                except:
                    pass
            await ctx.message.add_reaction(get_reaction_yes_no()["yes"])
            await asyncio.sleep(2.7)
            await ctx.message.delete()
        except:
            await ctx.send("Something went wrong unmuting members.")

    @commands.command(name="massmove", aliases=["mm"])
    @checks.admin_or_permissions(move_members=True)
    async def mass_move(self, ctx, from_channel: discord.VoiceChannel, to_channel: discord.VoiceChannel):
        """Move all members in specified voice channel to another.
        Requires Admin or move member permissions."""
        try:
            voice_list = list(from_channel.members)
            for member in voice_list:
                await member.move_to(to_channel)
        except discord.Forbidden:
            await ctx.send('I have no permission to move members.')
        except discord.HTTPException:
            await ctx.send('A error occured. Please try again')
        await ctx.message.add_reaction(get_reaction_yes_no()["yes"])
        await asyncio.sleep(2.7)
        await ctx.message.delete()

    @commands.command(name="massban")
    @checks.admin_or_permissions(ban_members=True)
    async def mass_ban(self, ctx, *members: discord.Member):
        """__**Warning!** Mass Ban given IDS.__"""
        n = 0
        for m in members:
            try:
                await m.ban(reason="Mass Ban")
                n += 1
            except:
                pass
        await ctx.send(f"Banned {n} members.")
    
    @commands.command(name="masskick")
    @checks.admin_or_permissions(kick_members=True)
    async def mass_kick(self, ctx, *members: discord.Member):
        """__**Warning!** Mass Kick given IDS.__"""
        n = 0
        for m in members:
            try:
                await m.kick(reason="Mass Kick")
                n += 1
            except:
                pass
        await ctx.send(f"Kicked {n} members.")


def setup(bot):
    bot.add_cog(Moderation(bot))

























