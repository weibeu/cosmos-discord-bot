import aiohttp
import discord
from discord.ext import commands
import asyncio
import re

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

    @commands.group(name="ban", invoke_without_command=True)
    @checks.admin_or_permissions(ban_members=True)
    async def _ban(self, ctx, member: discord.Member, reason: str = None):
        """Bans a member with provided optional reason.
        You can also check `;help ban preset` to add custom preset ban messages. Note: optional reason is latter to preset message."""
        files = []
        data = await self.bot.db_client.guilds[str(ctx.guild.id)].find_one(
            {'_id': 'settings'},
            {'presets.ban': '$'}
        )
        try:
            presets = data.get('presets')
            if presets:
                preset = presets.get('ban')
            else:
                preset = None
        except AttributeError:
            preset = None
        preset = preset or ''
        raw_reason = reason or ''
        reason = preset + raw_reason

        urls = re.findall(r'(?:http\:|https\:)?\/\/.*\.(?:png|jpg|gif)', reason)

        for url in urls:
            async with aiohttp.ClientSession() as ses:
                async with ses.get(url) as r:
                    img = await r.read()

            if ".png" in url.lower():
                filename = "tag.png"
            elif ".jpg" in url.lower():
                filename = "tag.jpg"
            elif ".gif" in url.lower():
                filename = "tag.gif"
            else:
                filename = "tag.png"

            file = discord.File(img, filename=filename)
            files.append(file)

            reason = reason.replace(url, "")

        try:
            if files:
                await member.send(f"You were **banned** from {ctx.guild.name}. **REASON:** {reason}", files=files)
            else:
                await member.send(f"You were **banned** from {ctx.guild.name}. **REASON:** {reason}")

            await member.ban(reason=f"{raw_reason} Moderator: {ctx.author.name}")

        except Exception as e:
            print(e)

        if files:
            await ctx.send(f"{member.name} was **banned** from **{ctx.guild.name}**. **REASON:** {reason}", files=files)
        else:
            await ctx.send(f"{member.name} was **banned** from **{ctx.guild.name}**. **REASON:** {reason}")

    @_ban.command(name="preset")
    async def set_ban_preset(self, ctx, *, message: str):
        """Preset custom message for ban command."""
        await self.bot.db_client.guilds[str(ctx.guild.id)].update_one(
            {'_id': 'settings'},
            {'$set': {'presets.ban': message}}
        )
        await ctx.message.add_reaction('✅')


    @commands.group(name="kick", invoke_without_command=True)
    @checks.admin_or_permissions(kick_members=True)
    async def _kick(self, ctx, member: discord.Member, reason: str = None):
        """Kicks a member with provided optional reason.
        You can also check `;help kick preset` to add custom preset kick messages. Note: optional reason is latter to preset message.
        """
        files = []
        data = await self.bot.db_client.guilds[str(ctx.guild.id)].find_one(
            {'_id': 'settings'},
            {'presets.kick': '$'}
        )
        try:
            presets = data.get('presets')
            if presets:
                preset = presets.get('kick')
            else:
                preset = None
        except AttributeError:
            preset = None
        preset = preset or ''
        raw_reason = reason or ''
        reason = preset + raw_reason

        urls = re.findall(r'(?:http\:|https\:)?\/\/.*\.(?:png|jpg|gif)', reason)

        for url in urls:
            async with aiohttp.ClientSession() as ses:
                async with ses.get(url) as r:
                    img = await r.read()

            if ".png" in url.lower():
                filename = "tag.png"
            elif ".jpg" in url.lower():
                filename = "tag.jpg"
            elif ".gif" in url.lower():
                filename = "tag.gif"
            else:
                filename = "tag.png"

            file = discord.File(img, filename=filename)
            files.append(file)

            reason = reason.replace(url, "")

        try:
            if files:
                await member.send(f"You were **kicked** from {ctx.guild.name}. **REASON:** {reason}", files=files)
            else:
                await member.send(f"You were **kicked** from {ctx.guild.name}. **REASON:** {reason}")

            await member.kick(reason=f"{raw_reason} Moderator: {ctx.author.name}")

        except Exception as e:
            print(e)

        if files:
            await ctx.send(f"{member.name} was **kicked** from. **REASON:** {reason}", files=files)
        else:
            await ctx.send(f"{member.name} was **kicked**. **REASON:** {reason}")

    @_kick.command(name="preset")
    async def set_kick_preset(self, ctx, *, message: str):
        """Preset custom message for kick command."""
        await self.bot.db_client.guilds[str(ctx.guild.id)].update_one(
            {'_id': 'settings'},
            {'$set': {'presets.kick': message}}
        )
        await ctx.message.add_reaction('✅')


    @commands.command(name="massban")
    @checks.admin_or_permissions(ban_members=True)
    async def mass_ban(self, ctx, *members: discord.Member):
        """__**Warning!** Mass Ban given IDS.__"""
        n = 0
        for m in members:
            try:
                await m.ban(reason=f"Mass Ban by {ctx.author.name}.")
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
                await m.kick(reason=f"Mass Kick by {ctx.author.name}.")
                n += 1
            except:
                pass
        await ctx.send(f"Kicked {n} members.")


def setup(bot):
    bot.add_cog(Moderation(bot))

























