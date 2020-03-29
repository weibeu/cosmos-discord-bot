from discord.ext import commands
import discord
from cogs.utils.checks import get_user, embed_perms
from cogs.utils import util

class Utilities(commands.Cog):
    """Some extra useful commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def uni(self, ctx, *, msg: str):
        """Convert to unicode emoji if possible. Ex: [p]uni :eyes:"""
        await ctx.send("`" + msg.replace("`", "") + "`")

    @commands.command()
    async def quote(self, ctx, *, msg: str = ""):
        """Quote a message. [p]help quote for more info.
        [p]quote - quotes the last message sent in the channel.
        [p]quote <words> - tries to search for a message in the server that contains the given words and quotes it.
        [p]quote <message_id> - quotes the message with the given message ID. Ex: [p]quote 302355374524644290 (enable developer mode to copy message IDs)
        [p]quote <user_mention_name_or_id> - quotes the last message sent by a specific user
        [p]quote <words> | channel=<channel_name> - quotes the message with the given words in a specified channel
        [p]quote <message_id> | channel=<channel_name> - quotes the message with the given message ID in a specified channel
        [p]quote <user_mention_name_or_id> | channel=<channel_name> - quotes the last message sent by a specific user in a specified channel
        """

        await ctx.message.delete()
        result = None
        channels = [ctx.channel] + [x for x in ctx.guild.channels if x != ctx.channel and type(x) == discord.channel.TextChannel]

        args = msg.split(" | ")
        msg = args[0]
        if len(args) > 1:
            channel = args[1].split("channel=")[1]
            channels = []
            for chan in ctx.guild.channels:
                if chan.name == channel or str(chan.id) == channel:
                    channels.append(chan)
                    break
            else:
                for guild in self.bot.guilds:
                    for chan in guild.channels:
                        if chan.name == channel or str(chan.id) == channel and type(chan) == discord.channel.TextChannel:
                            channels.append(chan)
                            break
            if not channels:
                return await ctx.send(self.bot.bot_prefix + "The specified channel could not be found.")

        user = get_user(ctx.message, msg)

        async def get_quote(msg, channels, user):
            for channel in channels:
                try:
                    if user:
                        async for message in channel.history(limit=500):
                            if message.author == user:
                                return message
                    if len(msg) > 15 and msg.isdigit():
                        async for message in channel.history(limit=500):
                            if str(message.id) == msg:
                                return message
                    else:
                        async for message in channel.history(limit=500):
                            if msg in message.content:
                                return message
                except discord.Forbidden:
                    continue
            return None

        if msg:
            result = await get_quote(msg, channels, user)
        else:
            async for message in ctx.channel.history(limit=1):
                result = message

        if result:
            if type(result.author) == discord.User:
                sender = result.author.name
            else:
                sender = result.author.nick if result.author.nick else result.author.name
            if embed_perms(ctx.message) and result.content:
                color = util.get_random_embed_color()
                em = discord.Embed(color=color, description=result.content, timestamp=result.created_at)
                em.set_author(name=sender, icon_url=result.author.avatar_url)
                footer = ""
                if result.channel != ctx.channel:
                    footer += "#" + result.channel.name

                if result.guild != ctx.guild:
                    footer += " | " + result.guild.name

                if footer:
                    em.set_footer(text=footer)
                await ctx.send(embed=em)
            elif result.content:
                await ctx.send('%s - %s```%s```' % (sender, result.created_at, result.content))
            else:
                await ctx.send(self.bot.bot_prefix + "Embeds cannot be quoted.")
        else:
            await ctx.send(self.bot.bot_prefix + 'No quote found.')

    @commands.command(name="migrate")
    async def migrate(self, ctx):

        roleshop = await self.bot.db_client.guilds[str(ctx.guild.id)].find_one({"_id": "role-shop"}, projection={"_id": False})
        members = await self.bot.db_client.guilds[str(ctx.guild.id)].find_one({"_id": "members"}, projection={"_id": False})

        print("fetched roleshop", len(roleshop))
        print("fetched members", len(members))

        # Migrate roleshop.
        data = [{int(role_id): int(points)} for role_id, points in roleshop.items()]
        await self.bot.db_client.cosmos.guilds.insert_one({"guild_id": ctx.guild.id, "roleshop": data})

        print("migrated roleshop")

        # Migrate points.
        for member_id in members:
            points = members[member_id].get("points")
            if points:
                await self.bot.db_client.cosmos.profiles.insert_one({"user_id": int(member_id), "guilds": {f"{ctx.guild.id}": {"points": {"points": points}}}})

        print("migrated points")

        await ctx.send("Done.")

def setup(bot):
    bot.add_cog(Utilities(bot))
