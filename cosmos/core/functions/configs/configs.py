import os

import discord

from .config import Config
from ..exceptions.initial import FatalError


class DiscordConfig(Config):

    NAME = "discord"
    PATH = "cfg/core/discord.yaml"

    def __init__(self):
        super().__init__()
        token = os.getenv("DiscordToken")   # Use token from environment if present.
        if token is not None:
            self.token = token


class CosmosConfig(Config):

    NAME = "cosmos"
    PATH = "cfg/core/cosmos.yaml"

    def __init__(self):
        self.prefixes = None
        super().__init__()


class PluginsConfig(Config):

    NAME = "plugins"
    PATH = "cfg/core/plugins.yaml"

    def __init__(self):
        super().__init__()


class LoggerConfig(Config):

    NAME = "logger"
    PATH = "cfg/core/logger.yaml"

    def __init__(self):
        super().__init__()


class DatabaseConfig(Config):

    NAME = "db"
    PATH = "cfg/core/database.yaml"

    def __init__(self):
        self.requires_auth = None
        self.username = None
        self.password = None
        self.host = None
        self.port = None
        self.uri = None
        self.raw = None
        super().__init__()
        if not self.requires_auth:
            self.host = self.host or "127.0.0.1"
            self.port = self.port or "27017"
            self.uri = f"mongodb://{self.host}:{self.port}/"
            self.__delattr__("username")
            self.__delattr__("password")
        elif None not in [self.username, self.password, self.host, self.port]:
            self.uri = f"mongodb://{self.username}:{self.password}@{self.host}:{self.port}/"
        else:
            self.__delattr__("username")
            self.__delattr__("password")
            self.__delattr__("host")
            self.__delattr__("port")
            if self.uri == "":
                raise FatalError("No valid credentials found to connect to the database.")


class SentryConfig(Config):

    NAME = "sentry"
    PATH = "cfg/core/sentry.yaml"

    def __init__(self):
        super().__init__()
        if hasattr(self, "release"):
            if self.release is None or "":
                self.__delattr__("release")


class CosmosEmotesConfig(Config):

    NAME = "emotes"
    PATH = "cfg/core/emotes.yaml"

    def __init__(self):
        super().__init__()


class CosmosColorScheme(Config):

    NAME = "color_scheme"
    PATH = "cfg/theme/color_scheme.yaml"

    def __init__(self):
        super().__init__()
        self._to_discord_color()

    def _to_discord_color(self):
        for color_type in self.raw:
            color_int = int(self.raw[color_type], 16)
            discord_color = discord.Color(color_int)
            self.__setattr__(color_type, discord_color)


class CosmosImagesConfig(Config):

    NAME = "images"
    PATH = "cfg/theme/images.yaml"

    def __init__(self):
        super().__init__()


class ImageProcessorClientConfig(Config):

    NAME = "image_processor"
    PATH = "cfg/core/image_processor.yaml"

    def __init__(self):
        super().__init__()
