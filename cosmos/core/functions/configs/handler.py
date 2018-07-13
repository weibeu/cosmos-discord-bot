import json

from cosmos.core.functions.configs.configs import *


class ConfigHandler(object):

    def __init__(self):
        self.discord = None
        self.cosmos = None
        self.plugins = None
        self._get_discord_config()
        self._get_cosmos_config()
        self._get_plugins_config()
        self._get_logger_config()

    @staticmethod
    def load(config_class, path):
        try:
            with open(path) as config_file:
                config = json.load(config_file)
                return config_class(config)
        except IOError:
            print(f"Unable to find '{path}.")
            raise IOError

    def _get_discord_config(self):
        print("Loading 'cfg/discord.json'.")
        self.discord = self.load(DiscordConfig, "cfg/discord.json")
        print("Done.")

    def _get_cosmos_config(self):
        print("Loading 'cfg/cosmos.json'.")
        self.cosmos = self.load(CosmosConfig, "cfg/cosmos.json")
        print("Done.")

    def _get_plugins_config(self):
        print("Loading 'cfg/plugins.json'.")
        self.plugins = self.load(PluginsConfig, "cfg/plugins.json")
        print("Done.")

    def _get_logger_config(self):
        print("Loading 'cfg/logger.json'.")
        self.logger = self.load(LoggerConfig, "cfg/logger.json")
        print("Done.")
