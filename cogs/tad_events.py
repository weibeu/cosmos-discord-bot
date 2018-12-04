import time
import discord
import asyncio
import random

class SantaEvent(object):

    GUILD_ID = 244998983112458240
    ROLE_ID = 518971059756859393
    EMOJI = '🎁'
    WAIT_FOR = 7

    def __init__(self, bot):
        self.bot = bot
        self.guild = None
        self.role = None

    async def fetch_objects(self):
        await self.bot.wait_until_ready()
        self.guild = self.bot.get_guild(GUILD_ID)
        self.role = discord.utils.get(self.guild.roles, id=ROLE_ID)

    async def __local_check(self, ctx):
        return ctx.guild.id == GUILD_ID

    async def on_message(self, message):
        if message.author.bot:
            return
        if message.attachments != []:
            return
        if message.guild.id != GUILD_ID:
            return
        if time.time() - self.time <= 2820:
            return
        def check(reaction, user):
            if reaction.emoji != EMOJI or user.bot:
                return False
            if reaction.message.id != message.id:
                return False
            if user.id == self.bot.user.id:
                return False
            return True

        if random.randint(1, 100) <= 2:
            await message.add_reaction(EMOJI)
            await asyncio.sleep(WAIT_FOR)
            await message.clear_reactions()
            for r in message.reactions:
                if r.emoji == EMOJI:
                    reaction = r
                else:
                    reaction = None
            members = []
            async for m in reaction.users():
                if self.role not in m.roles:
                    members.append(m)
            
