import os

import discord

from .config import Config
from ..exceptions.initial import FatalError


class DiscordConfig(Config):

    NAME = "discord"
    PATH = "cfg/core/discord.yaml"

    def __init__(self):
        self.client_id = None
        super().__init__()
        self.token = os.getenv("DISCORD_TOKEN") or self.token   # Use token from environment if present.
        self.invite_url = discord.utils.oauth_url(str(self.client_id), discord.Permissions(8))


class CosmosConfig(Config):

    NAME = "cosmos"
    PATH = "cfg/core/cosmos.yaml"

    def __init__(self):
        super().__init__()
        self.prefixes = [os.getenv("COSMOS_PREFIX", *self.prefixes)]


class PluginsConfig(Config):

    NAME = "plugins"
    PATH = "cfg/core/plugins.yaml"


class LoggerConfig(Config):

    NAME = "logger"
    PATH = "cfg/core/logger.yaml"


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
        self.database = os.getenv("MONGODB_DATABASE") or self.database
        self.username = os.getenv("MONGODB_USERNAME") or self.username
        self.password = os.getenv("MONGODB_PASSWORD") or self.password
        self.uri = os.getenv("MONGODB_URI") or self.uri
        if not (self.requires_auth or self.uri):
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
        self.dsn = os.getenv("SENTRY_DSN") or self.dsn
        self.environment = os.getenv("ENVIRONMENT") or self.environment
        self.raw.update({"environment": self.environment})
        if hasattr(self, "release"):
            if self.release is None or "":
                self.__delattr__("release")


class CosmosEmotesConfig(Config):

    NAME = "emotes"
    PATH = "cfg/core/emotes.yaml"


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


class ImageProcessorClientConfig(Config):

    NAME = "image_processor"
    PATH = "cfg/core/image_processor.yaml"


class CosmosMetaInformation(Config):

    NAME = "info"
    PATH = "cfg/core/information.yaml"
