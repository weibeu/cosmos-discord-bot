import json
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


class Config(object):

    def __init__(self):
        self.discord = None
        self.cosmos = None
        self._get_discord_config()
        self._get_cosmos_config()

    def _get_discord_config(self):
        try:
            with open("cfg/discord.json") as config_file:
                discord_config = json.load(config_file)
                self.discord = DiscordConfig(discord_config)
        except IOError:
            print("Unable to find 'cfg/discord.json'.")
            raise IOError

    def _get_cosmos_config(self):
        try:
            with open("cfg/cosmos.json") as config_file:
                cosmos_config = json.load(config_file)
                self.cosmos = CosmosConfig(cosmos_config)
        except IOError:
            print("Unable to find 'cfg/cosmos.json'.")
            raise IOError

    def _get_plugins_config(self):
        try:
            with open("cfg/plugins.json") as config_file:
                discord_config = json.load(config_file)
                self.plugins = PluginsConfig(discord_config)
        except IOError:
            print("Unable to find 'cfg/plugins.json'.")
