import discord
from discord.ext import commands
from cogs.utils.util import get_reaction_yes_no, get_random_embed_color

class TAD(object):
    """A custom class for tad server."""

    def __init__(self, bot):
        self.bot = bot
        #self.rules = self.bot.get_channel(452702379293540372)
        #self.server_guide = self.bot.get_channel(269610314578788363)



        #bot.loop.create_task(self.rotate())

    '''async def rotate(self):
        await self.bot.wait_until_ready()
        m_rules = await self.rules.get_message(452756009811968001)
        m_punishments = await self.rules.get_message(452756043114479629)
        m_banner = await self.server_guide.get_message(452822879067832320)
        m_info = await self.server_guide.get_message(452822935049338881)'''

    async def __local_check(self, ctx):
        return ctx.guild.id in [244998983112458240]

    async def on_message(self, message):

        '''if message.author.id == 280883146872979456 and message.attachments != []:
            await message.delete()
            await message.channel.send("lol steve fuck off")'''

    @commands.group(hidden=True)
    async def study(self, ctx):
        """Avoid yourself from distractions and get yourself locked in study room."""
        if ctx.invoked_subcommand is None:
            role = discord.utils.get(ctx.guild.roles, id=447945813100986379)
            await ctx.author.add_roles(role, reason=ctx.author.name+" wanted to study.")
            await ctx.message.add_reaction(get_reaction_yes_no()["yes"])

    @study.command(hidden=True)
    async def stop(self, ctx):
        """Done studying or wanna take some rest? Use this command to join back the real fun."""
        role = discord.utils.get(ctx.guild.roles, id=447945813100986379)
        await ctx.author.remove_roles(role, reason=ctx.author.name+" stopped studying.")
        await ctx.message.add_reaction(get_reaction_yes_no()["yes"])

def setup(bot):
    bot.add_cog(TAD(bot))
