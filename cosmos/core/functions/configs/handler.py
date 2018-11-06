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
        return config_class(self.bot.utilities.file_handler.get_file_data(path))

    def _get_all(self):
        self.__get_discord_config()
        self.__get_cosmos_config()
        self.__get_plugins_config()
        self.__get_logger_config()
        self.__get_database_config()
        self.__get_sentry_config()

    def __get_discord_config(self):
        self.discord = self.load(DiscordConfig, "core/discord.yaml")

    def __get_cosmos_config(self):
        self.cosmos = self.load(CosmosConfig, "core/cosmos.yaml")

    def __get_plugins_config(self):
        self.plugins = self.load(PluginsConfig, "core/plugins.yaml")

    def __get_logger_config(self):
        self.logger = self.load(LoggerConfig, "core/logger.yaml")

    def __get_database_config(self):
        self.db = self.load(DatabaseConfig, "core/database.yaml")

    def __get_sentry_config(self):
        self.sentry = self.load(SentryConfig, "core/sentry.yaml")
