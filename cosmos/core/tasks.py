from discord.ext import commands

from .functions import *
from .utilities import *


class InitialTasks(commands.Bot):

    def __init__(self):
        self._init_time()
        self._init_utilities()
        self._init_configs()
        super().__init__(
            command_prefix=commands.when_mentioned_or(*self.configs.cosmos.prefixes),
            case_insensitive=True
        )
        self._init_logger()
        self._init_exception_handler()
        self._init_database()
        self._init_caches()
        self._init_emotes()
        self._init_plugins()
        self._init_theme()

    @Time.calc_time
    def _init_time(self):
        print("Initialising Cosmos time.")
        self.time = Time()

    @Time.calc_time
    def _init_utilities(self):
        print("Initialising utilities.")
        self.utilities = Utility(self)

    @Time.calc_time
    def _init_configs(self):
        print("Initialising configs.")
        self.configs = ConfigHandler(self)

    @Time.calc_time
    def _init_logger(self):
        print("Initialising logger.")
        self.log = LoggerHandler(self)

    @Time.calc_time
    def _init_exception_handler(self):
        self.log.info("Initialising exception handler.")
        self.eh = ExceptionHandler(self)
        try:
            self.eh.sentry.init(**self.configs.sentry.raw)
        except self.eh.sentry.utils.BadDsn:
            self.log.error("Invalid sentry DSN provided.")

    @Time.calc_time
    def _init_database(self):
        self.log.info("Initialising database.")
        self.db_client = DatabaseClient(self)
        self.db = self.db_client.db

    @Time.calc_time
    def _init_caches(self):
        self.log.info("Initialising caches.")
        self.cache = CacheHandler(self)

    @Time.calc_time
    def _init_emotes(self):
        self.log.info("Initialising cosmos emotes.")
        self.emotes = CosmosEmotes(self)

    @Time.calc_time
    def _init_plugins(self):
        self.log.info("Initialising plugins.")
        self.plugins = PluginHandler(self)
        self.plugins.load_all()    # Here since Plugin requires self.bot.plugins to load itself.

    @Time.calc_time
    def _init_theme(self):
        self.log.info("Initialising cosmos theme.")
        self.theme = CosmosTheme(self)
