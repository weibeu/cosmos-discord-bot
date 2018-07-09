import os

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
