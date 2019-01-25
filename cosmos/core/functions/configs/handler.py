from .configs import *


class ConfigHandler(object):

    def __init__(self, bot):
        self.bot = bot
        self.discord: DiscordConfig = None
        self.cosmos: CosmosConfig = None
        self.plugins: PluginsConfig = None
        self.logger: LoggerConfig = None
        self.db: DatabaseConfig = None
        self.sentry: SentryConfig = None
        self.emotes: CosmosEmotesConfig = None
        self.color_scheme: CosmosColorScheme = None
        self._get_all()

    def _get_all(self):
        self.discord = DiscordConfig()
        self.cosmos = CosmosConfig()
        self.plugins = PluginsConfig()
        self.logger = LoggerConfig()
        self.db = DatabaseConfig()
        self.sentry = SentryConfig()
        self.emotes = CosmosEmotesConfig()
        self.color_scheme = CosmosColorScheme()
