import datetime
import functools

from ... import Cog


def logger_event(*args, **kwargs):

    def decorator(function):
        @Cog.listener(*args, **kwargs)
        @functools.wraps(function)
        async def wrapper(cog, *_args):
            guild_profile = await cog.bot.guild_cache.get_profile(_args[0].guild.id)
            logger = guild_profile.get_logger(function.__name__)
            if not logger:
                return
            embed = cog.embed(title=function.__name__.lstrip("on_").replace("_", " ").title())
            embed.timestamp = datetime.datetime.now()
            embed = await function(cog, embed, *_args)
            if not embed:
                return
            await logger.channel.send(embed=embed)
        return wrapper

    return decorator


class LoggerEvents(Cog):

    # TODO: Add reactions based actions.

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.loggers = [name for name, _ in self.get_listeners()]

    @property
    def embed(self):
        return self.bot.theme.embeds.primary

    @logger_event()
    async def on_message_delete(self, embed, message):
        if message.author.bot:
            return
        embed.add_field(name="Deleted Message", value=message.clean_content, inline=False)
        embed.add_field(name="Author", value=message.author.mention)
        embed.add_field(name="Author Name", value=message.author)
        embed.add_field(name="Author ID", value=message.author.id)
        embed.add_field(name="From Channel", value=message.channel.mention)
        return embed

    @logger_event()
    async def on_bulk_message_delete(self, embed, messages):
        embed.add_field(name="Messages Deleted", value=f"{len(messages)} messages.")
        if messages:
            embed.add_field(name="From Channel", value=messages[0].channel.mention)
        return embed

    @logger_event()
    async def on_message_edit(self, embed, before, after):
        if after.author.bot:
            return
        embed.add_field(name="Before Edit", value=before.clean_content)
        embed.add_field(name="After Edit", value=after.clean_content)
        embed.add_field(name="Author", value=after.author.mention)
        embed.add_field(name="Author Name", value=after.author)
        embed.add_field(name="Author ID", value=after.author.id)
        embed.add_field(name="In Channel", value=after.channel.mention)
        embed.add_field(name="Actual Message", value=f"[Jump to the message]({after.jump_url})")
        return embed

    @logger_event()
    async def on_guild_channel_pins_update(self, embed, channel, _):
        embed.title = "Message Pinned"
        message = (await channel.pins())[0]
        embed.add_field(name="Message Content", value=message.clean_content, inline=False)
        embed.add_field(name="Author", value=message.author.mention)
        embed.add_field(name="In Channel", value=channel.mention)
        embed.add_field(name="Actual Message", value=f"[Jump to the message]({message.jump_url})")
        return embed

    @logger_event()
    async def on_member_join(self, embed, member):
        embed.add_field(name="Member", value=member.mention)
        embed.add_field(name="Member Name", value=member)
        embed.add_field(name="Member ID", value=f"`{member.id}`")
        embed.add_field(name="Account Created", value=f"on {member.created_at.strftime('%d %B %Y')}")
        embed.set_thumbnail(url=member.avatar_url)
        return embed

    @logger_event()
    async def on_member_remove(self, embed, member):
        embed.title = "Member Left"
        embed.color = int("0xF44336", 16)
        embed.add_field(name="Member Name", value=member)
        embed.add_field(name="Member ID", value=f"`{member.id}`")
        embed.set_thumbnail(url=member.avatar_url)
        return embed

    # @logger_event()
    # async def on_member_ban(self, embed, guild, user):
    #     pass
    #
    # @logger_event()
    # async def on_member_unban(self, embed, guild, user):
    #     pass

    @logger_event()
    async def on_moderation(self, embed, member, action):
        pass
