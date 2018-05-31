import discord
from discord.ext import commands
from cogs.utils.util import get_reaction_yes_no

class TAD(object):
    """A custom class for tad server."""

    def __init__(self, bot):
        self.bot = bot

    async def __local_check(self, ctx):
        return ctx.guild.id in [244998983112458240, 434065022000431124]

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


    @commands.command(hidden=True)
    @commands.is_owner()
    async def rules(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed()
        embed.set_author(name="RULES")
        embed.add_field(name="<a:pointer:440925289317531668>    __** Discord tos apply**__", value="ANY violation will result in an immediate ban and report to Discord: [Discord Tos](https://discordapp.com/tos)", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    __** Be respectful of others**__", value="Bullying, cussing, harassment, racism, sexism, or any sort of discrimination will not be tolerated.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    __** Use common sense**__", value="If someone is uncomfortable with something, stop. Also refrain from discussing real-life Politics, religion, killing or suicide.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    __** Do not spam**__", value="Do not send random or irrelevant messages. This includes text, copypastas, Emojis, images, links, literally anything. This applies to VC too, Ear-raping or being obnoxious in VC will result in punishment.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    __** DRAMA FREE ZONE**__", value="Do not create server drama or take part in it. If you have any problem with the server, talk to the staff via DMs.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    __** No NSFW **__", value="Keep any and all 18+ flirting, overly sexual discussion, recommendations, images, links, etc. in DM’s only.  NSFW content is not allowed on The Anime Discord.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    __** No Mini Modding **__", value="Leave all the moderation to Staff. If there is someone causing any trouble DM/Ping a Celstial Dragon.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    __** Do not advertise or self-promote. **__", value="This is not a place to advertise your server, YouTube, Twitch etc. Do not solicit other users for donations or money. You will receive a permanent ban if we determine you are using the server for those purposes.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    __** No inappropriate profiles **__", value="Usernames or avatars considered to be racist, discriminatory, overly lewd or intended to mimic another user are not tolerated and will result in an immediate ban.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    __** Speak English. **__", value="This is an English speaking server.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    __** Respect channel topics and rules. **__", value="Every channel on this server has its own specific guidelines and rules. They can be found in the channel description.", inline=False)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.colour=int("0x"+"E91E63", 16)
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(TAD(bot))
