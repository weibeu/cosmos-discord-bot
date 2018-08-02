import json

from cosmos.core.functions.configs.configs import *


class ConfigHandler(object):

    def __init__(self):
        self.discord = None
        self.cosmos = None
        self.plugins = None
        self.logger = None
        self.db = None
        self._get_all()

    @staticmethod
    def load(config_class, path):
        if not path.startswith("cfg/"):
            path = f"cfg/{path}"
        try:
            with open(path) as config_file:
                config = json.load(config_file)
                return config_class(config)
        except IOError:
            print(f"Unable to find '{path}.")
            raise IOError

    def _get_all(self):
        self._get_discord_config()
        self._get_cosmos_config()
        self._get_plugins_config()
        self._get_logger_config()
        self._get_database_config()

    def _get_discord_config(self):
        self.discord = self.load(DiscordConfig, "discord.json")

    def _get_cosmos_config(self):
        self.cosmos = self.load(CosmosConfig, "cosmos.json")

    def _get_plugins_config(self):
        self.plugins = self.load(PluginsConfig, "plugins.json")

    def _get_logger_config(self):
        self.logger = self.load(LoggerConfig, "logger.json")

    def _get_database_config(self):
        self.db = self.load(DatabaseConfig, "database.json")
