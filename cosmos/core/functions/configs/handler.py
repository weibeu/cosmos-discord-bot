import yaml
import json

from cosmos.core.functions.configs.configs import *


class ConfigHandler(object):

    def __init__(self, bot):
        self.bot = bot
        self.discord = None
        self.cosmos = None
        self.plugins = None
        self.logger = None
        self.db = None
        self.sentry = None
        self._get_all()

    def load(self, config_class, path):
        if not path.startswith("cfg/"):
            path = f"cfg/{path}"
        try:
            with open(path) as config_file:
                if path.endswith(".json"):
                    config = json.load(config_file)
                elif path.endswith(".yaml") or path.endswith(".yml"):
                    config = yaml.load(config_file)
                else:
                    print(f"Unsupported config file specified. Ignoring {path}.")
                return config_class(config)
        except IOError:
            print(f"Unable to find specified '{path}.")
            raise IOError

    def _get_all(self):
        self._get_discord_config()
        self._get_cosmos_config()
        self._get_plugins_config()
        self._get_logger_config()
        self._get_database_config()
        self._get_sentry_config()

    def _get_discord_config(self):
        self.discord = self.load(DiscordConfig, "core/discord.yaml")

    def _get_cosmos_config(self):
        self.cosmos = self.load(CosmosConfig, "core/cosmos.yaml")

    def _get_plugins_config(self):
        self.plugins = self.load(PluginsConfig, "core/plugins.yaml")

    def _get_logger_config(self):
        self.logger = self.load(LoggerConfig, "core/logger.yaml")

    def _get_database_config(self):
        self.db = self.load(DatabaseConfig, "core/database.yaml")

    def _get_sentry_config(self):
        self.sentry = self.load(SentryConfig, "core/sentry.yaml")
