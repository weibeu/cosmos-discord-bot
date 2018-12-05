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

    def _get_all(self):
        self.discord = DiscordConfig()
        self.cosmos = CosmosConfig()
        self.plugins = PluginsConfig()
        self.logger = LoggerConfig()
        self.db = DatabaseConfig()
        self.sentry = SentryConfig()
