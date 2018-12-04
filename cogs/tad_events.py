import time
import discord
import asyncio
import random

from cogs.utils.db import give_points
from cogs.utils.util import get_random_embed_color

class SantaEvent(object):

    GUILD_ID = 390134592507609088   # 244998983112458240
    ROLE_ID = 476719309901791232    # 518971059756859393
    EMOJI = '🎁'
    COOLDOWN = 25
    CHANCE = 100
    WAIT_FOR = 7
    SANTA_GIF = "https://media1.giphy.com/media/3oriNS6RGNct2MZWJq/giphy.gif"

    def __init__(self, bot):
        self.bot = bot
        self.guild = None
        self.role = None
        self.bot.loop.create_task(self.fetch_objects())

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
        if time.time() - self.time <= COOLDOWN:
            return

        if random.randint(1, 100) <= CHANCE:
            await message.add_reaction(EMOJI)
            await asyncio.sleep(WAIT_FOR)
            await message.clear_reactions()
            for r in message.reactions:
                if r.emoji == EMOJI:
                    reaction = r
                else:
                    reaction = None
            members = []
            role_members = []
            async for m in reaction.users():
                if self.role in m.roles:
                    role_members.append(m)
                else:
                    members.append(m)
            
            points_common = random.choice(range(50, 61))
            points_uncommon = random.choice(range(61, 101))
            points_rare = random.choice(range(101, 200))
            points_leg = random.choice(range(200, 301))
            points = random.choice([points_common]*90+[points_uncommon]*7+[points_rare]*2+[points_leg])

            winner = random.choice(role_members)
            await winner.add_roles(self.role, reason="Gift from TAD's Santa Lil Neko")
            winner_points = random.choice([points_common]*40+[points_uncommon]*30+[points_rare]*20+[points_leg]*10)
            await give_points(str(message.guild.id), str(winner.id), winner_points)
            role_members.remove(winner)
            embed = discord.Embed(title=f"{EMOJI} Gifts!", colour=get_random_embed_color())
            embed.set_footer(text=f"Congrats {winner.name}!", icon_url=winner.avatar_url)
            embed.set_author(name="Santa Neko", icon_url=SANTA_GIF) 
            description = "🏆    __**{winner.name}**__    {self.role.mention} & +{winner_points}\n\n"
            members += role_members
            for m in members:
                m_points = random.choice([points_common]*80+[points_uncommon]*15+[points_rare]*3+[points_leg]*2)
                await give_points(str(message.guild.id), str(m.id), m_points)
                description += "🤶    {m.name}    +{m_points}\n"
            await message.channel.send(embed=embed)


def setup(bot):
    bot.add_cog(SantaEvent(bot))
