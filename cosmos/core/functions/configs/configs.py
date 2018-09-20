import os

from cosmos.core.functions.configs.config import Config
from cosmos.core.functions.exceptions.initial import FatalError

class DiscordConfig(Config):

    def __init__(self, client_config):
        super().__init__(client_config)
        token = os.getenv("DiscordToken")   # Use token from environment if present.
        if token is not None:
            self.token = token

class CosmosConfig(Config):

    def __init__(self, cosmos_config):
        super().__init__(cosmos_config)

class PluginsConfig(Config):

    def __init__(self, plugins_config):
        super().__init__(plugins_config)

class LoggerConfig(Config):

    def __init__(self, logger_config):
        super().__init__(logger_config)

class DatabaseConfig(Config):

    def __init__(self, database_config):
        self.requires_auth = None
        self.username = None
        self.password = None
        self.host = None
        self.port = None
        self.uri = None
        self.raw = None
        super().__init__(database_config)
        if not self.requires_auth:
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

    def __init__(self, sentry_config):
        super().__init__(sentry_config)
