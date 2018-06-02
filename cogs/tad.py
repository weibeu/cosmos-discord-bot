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
        embed.title="RULES"
        embed.add_field(name="<a:pointer:440925289317531668>    ** Discord tos apply**", value="ANY violation will result in an immediate ban and report to Discord: [Discord Tos](https://discordapp.com/tos)", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    ** Be respectful of others**", value="Bullying, cussing, harassment, racism, sexism, or any sort of discrimination will not be tolerated.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    ** Use common sense**", value="If someone is uncomfortable with something, stop. Also refrain from discussing real-life Politics, religion, killing or suicide.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    ** Do not spam**", value="Do not send random or irrelevant messages. This includes text, copypastas, Emojis, images, links, literally anything. This applies to VC too, Ear-raping or being obnoxious in VC will result in punishment.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    ** DRAMA FREE ZONE**", value="Do not create server drama or take part in it. If you have any problem with the server, talk to the staff via DMs.__**No roleplay**__", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    ** No NSFW **", value="Keep any and all 18+ flirting, overly sexual discussion, recommendations, images, links, etc. in DM’s only.  NSFW content is not allowed on The Anime Discord.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    ** No Mini Modding **", value="Leave all the moderation to Staff. If there is someone causing any trouble DM/Ping a Celstial Dragon.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    ** Do not advertise or self-promote. **", value="This is not a place to advertise your server, YouTube, Twitch etc. Do not solicit other users for donations or money. You will receive a permanent ban if we determine you are using the server for those purposes.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    ** No inappropriate profiles **", value="Usernames or avatars considered to be racist, discriminatory, overly lewd or intended to mimic another user are not tolerated and will result in an immediate ban.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    ** Speak English. **", value="This is an English speaking server.", inline=False)
        embed.add_field(name="<a:pointer:440925289317531668>    ** Respect channel topics and rules. **", value="Every channel on this server has its own specific guidelines and rules. They can be found in the channel description.", inline=False)
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.colour=int("0x"+"E91E63", 16)
        await ctx.send(embed=embed)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def rules(self, ctx):
        await ctx.message.delete()
        embed = discord.Embed()
        embed.title = "PUNISHMENTS"
        embed.description = "If one or more of the rules are broken by a member, the staff will be obligated to follow the bad doggo protocol:\n\t<a:arrow:437323076330586113> 😟 = First warning, lasts for 10 days. `+15 mins Doggo`\n\t<a:arrow:437323076330586113> 😠 = Second warning, lasts for 20 days. `3 hours Doggo`\n\t<a:arrow:437323076330586113> 😡 = Third warning, lasts for 40 days. `24 hours Doggo`\n\n__ If a member breaks the rules after being given 3rd warning, they will receive a **permanent ban**.__\n**Note:**\tA member may get banned despite not having above three warnings if their stay here causes a severe harm to the server or members in any possible manner."
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon_url)
        embed.colour=int("0x"+"E91E63", 16)

def setup(bot):
    bot.add_cog(TAD(bot))
