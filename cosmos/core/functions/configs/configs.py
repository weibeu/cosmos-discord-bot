import os
from cosmos.core.functions.exceptions.initial import FatalError

class DiscordConfig(object):

    def __init__(self, client_config):
        self.raw = client_config
        for config in self.raw:
            self.__setattr__(config, self.raw[config])
        token = os.getenv("DiscordToken")   # Use token from environment if present.
        if token is not None:
            self.token = token

class CosmosConfig(object):

    def __init__(self, cosmos_config):
        self.raw = cosmos_config
        for config in self.raw:
            self.__setattr__(config, self.raw[config])

class PluginsConfig(object):

    def __init__(self, plugins_config):
        self.raw = plugins_config
        for config in self.raw:
            self.__setattr__(config, self.raw[config])

class LoggerConfig(object):

    def __init__(self, logger_config):
        self.raw = logger_config
        for config in self.raw:
            self.__setattr__(config, self.raw[config])

class DatabaseConfig(object):

    def __init__(self, database_config):
        self.requires_auth = None
        self.username = None
        self.password = None
        self.host = None
        self.port = None
        self.uri = None
        self.raw = database_config
        for config in self.raw:
            if self.raw[config] == "":
                self.raw[config] = None
            self.__setattr__(config, self.raw[config])
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

class SentryConfig(object):

    def __init__(self, sentry_config):
        self.raw = sentry_config
        for config in self.raw:
            self.__setattr__(config, self.raw[config])
