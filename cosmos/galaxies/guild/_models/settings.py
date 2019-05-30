from abc import ABC

from discord import Color
from .base import CosmosGuildBase


class WelcomeBannerSettings(CosmosGuildBase, ABC):

    def __init__(self, **kwargs):
        raw_welcome_settings = kwargs.get("welcome", dict())
        raw_banner_settings = raw_welcome_settings.get("banner", dict())
        self.welcome_banner_url = raw_banner_settings.get("url", str())
        self.welcome_banner_text = raw_banner_settings.get("text", str())
        self.__welcome_banner_channel_id = raw_banner_settings.get("channel", int())
        self.welcome_banner_enabled = raw_banner_settings.get("enabled", False)

    @property
    def welcome_banner_channel(self):
        return self.guild.get_channel(self.__welcome_banner_channel_id)

    async def set_welcome_banner(self, banner_url, text, channel_id):
        self.welcome_banner_url = banner_url
        self.welcome_banner_text = text
        self.__welcome_banner_channel_id = channel_id
        self.welcome_banner_enabled = False

        await self.collection.update_one(
            self.document_filter, {"$set": {
                "settings.welcome.banner.url": self.welcome_banner_url,
                "settings.welcome.banner.text": self.welcome_banner_text,
                "settings.welcome.banner.channel": self.__welcome_banner_channel_id,
                "settings.welcome.banner.enabled": self.welcome_banner_enabled
            }}
        )

    async def enable_welcome_banner(self, enable=True):
        self.welcome_banner_enabled = enable

        await self.collection.update_one(self.document_filter, {"$set": {"settings.welcome.banner.enabled": enable}})

# TODO: Don't pass whole document. Rather pass the embedded document of only that model to remove raw_..._settings.


class ThemeSettings(object):

    def __init__(self, guild_profile, **kwargs):
        self.__profile = guild_profile
        raw_theme_settings = kwargs.get("theme", dict())
        color = raw_theme_settings.get("color")
        if color is not None:
            self.color = Color(color)
        else:
            self.color = None

    async def set_color(self, color):
        self.color = color

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$set": {"settings.theme.color": self.color.value}}
        )


class GuildSettings(WelcomeBannerSettings, ABC):

    def __init__(self, **kwargs):
        raw_settings = kwargs.get("settings", dict())
        super().__init__(**raw_settings)
        self.theme = ThemeSettings(self, **raw_settings)
