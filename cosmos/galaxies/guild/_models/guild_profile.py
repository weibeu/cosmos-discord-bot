import discord

from io import BytesIO
from cosmos import exceptions

from .levels import Levels
from .settings import GuildSettings
from .roleshop import GuildRoleShop
from .reactions import GuildReactions


class CosmosGuild(GuildSettings, GuildRoleShop):

    @property
    def plugin(self):
        return self.__plugin

    @property
    def id(self):
        return self.__id

    @classmethod
    def from_document(cls, plugin, document: dict):
        return cls(plugin, **document)

    async def fetch_member_profile(self, _id):
        return await self.plugin.bot.profile_cache.get_guild_profile(_id, self.id)

    def __init__(self, plugin, **kwargs):
        self.__plugin = plugin
        self.__id = kwargs["guild_id"]
        self.is_prime = kwargs.get("is_prime", False)
        GuildSettings.__init__(self, **kwargs)
        GuildRoleShop.__init__(self, **kwargs)
        self.levels = Levels(self, **kwargs)
        self.reactions = GuildReactions(self, kwargs.get("reactions", dict()))

    async def send_welcome_banner(self, member, channel: discord.TextChannel = None):
        banner_format = self.welcome_banner_url.split(".")[-1]
        if banner_format.lower() == "gif" and not self.is_prime:
            raise exceptions.GuildNotPrime
        channel = channel or self.welcome_banner_channel
        options = dict()
        if self.theme.color:
            options["border_color"] = options["font_color"] = options["avatar_border_color"] = str(self.theme.color)
        banner_bytes = await self.plugin.bot.image_processor.discord.get_welcome_banner(
            self.welcome_banner_url, str(member.avatar_url), member.name, self.welcome_banner_text, **options)
        file = discord.File(BytesIO(banner_bytes), filename=f"{self.plugin.data.settings.banner_name}.{banner_format}")
        await channel.send(file=file)
