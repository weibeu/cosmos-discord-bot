import discord
import asyncio
import time
import random

from cogs.utils import db
from discord.ext import commands
from cogs.utils import checks


class Event(object):

    def __init__(self, bot):
        self.bot = bot
        self.messages = []
        self.disabled_channels = {}
        self.time = time.time()
        bot.loop.create_task(self.get_settings())

    async def get_settings(self):
        await self.bot.wait_until_ready()
        self.disabled_channels = await db.get_spook_data(self.bot.guilds)

    async def on_message(self, message):
        if message.author.bot:
            return
        if message.attachments != []:
            return
        if str(message.guild.id) in self.disabled_channels:
            if message.channel.id in self.disabled_channels[str(message.guild.id)]:
                return
        if time.time() - self.time < 1200:
            return
        
        def check(reaction, user):
            if reaction.emoji != '🎃' or user.bot:
                return False
            if reaction.message.id != message.id:
                return False
            if user.id == self.bot.user.id:
                return False
            return True

        if random.randint(1, 100) <= 2:
            await message.add_reaction('🎃')
            points_common = random.choice(range(50, 61))
            points_uncommon = random.choice(range(61, 101))
            points_rare = random.choice(range(101, 200))
            points_leg = random.choice(range(200, 301))
            points = random.choice([points_common]*90+[points_uncommon]*7+[points_rare]*2+[points_leg])
            try:
                reaction, member = await self.bot.wait_for('reaction_add', check=check, timeout=7)
                await db.give_points(str(message.guild.id), str(member.id), points)
                await message.channel.send(f"{member.mention} 👌 + {points} points!")
                await message.clear_reactions()
                await message.remove_reaction('🎃', reaction.message.author)
                self.time = time.time()
            except asyncio.TimeoutError:
                await message.clear_reactions()

    @commands.group(name="spook")
    @checks.is_mod()
    async def spook(self, ctx):
        """Festive reaction spawns which credits guild points."""
        if ctx.invoked_subcommand is None:
            return
    @spook.command(name="enable")
    async def spook_enable(self, ctx, channel: discord.TextChannel = None):
        """Enable spooky reactions in current or specified channel."""
        channel = channel or ctx.channel
        await db.spook_enable(str(ctx.guild.id), ctx.channel.id)
        l = self.disabled_channels[str(ctx.guild.id)]
        try:
            l.remove(ctx.channel.id)
        except ValueError:
            await ctx.send("Spook is already enabled in current channel.")
            return
        self.disabled_channels[str(ctx.guild.id)] = l
        await ctx.send(f"Spook enabled in {channel.mention}.")

    @spook.command(name="disable")
    async def spook_disable(self, ctx, channel: discord.TextChannel = None):
        """Disable spooky reactions in current or specified channel."""
        channel = channel or ctx.channel
        await db.spook_disable(str(ctx.guild.id), ctx.channel.id)
        l = self.disabled_channels[str(ctx.guild.id)]
        l.append(ctx.channel.id)
        self.disabled_channels[str(ctx.guild.id)] = l
        await ctx.send(f"Spook disabled in {channel.mention}.")

def setup(bot):
    bot.add_cog(Event(bot))
