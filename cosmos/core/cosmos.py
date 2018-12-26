import discord
from discord.ext import commands

from .functions.cacher.handler import CacheHandler
from .functions.configs.handler import ConfigHandler
from .functions.database.database import Database
from .functions.exceptions.handler import ExceptionHandler
from .functions.logger.handler import LoggerHandler
from .functions.plugins.handler import PluginHandler
from .utilities.handler import Utility
from .utilities.time import Time


class Cosmos(commands.Bot):

    def __init__(self, token=None, client_id=None, prefixes=None):
        self.time = None
        self.configs = None
        self.eh = None
        self.log = None
        self.cache = None
        self.db = None
        self.plugins = None
        self._init_time()
        self._init_utilities()
        self._init_configs()
        super().__init__(
            command_prefix=commands.when_mentioned_or(*self.configs.cosmos.prefixes)
        )
        self._init_logger()
        self._init_exception_handler()
        self._init_caches()
        self._init_database()
        self._init_plugins()
        self.configs.discord.token = token or self.configs.discord.token
        self.configs.discord.client_id = client_id or self.configs.discord.client_id
        self.configs.discord.prefixes = prefixes or self.configs.cosmos.prefixes

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
    def _init_caches(self):
        self.log.info("Initialising caches.")
        self.cache = CacheHandler(self)

    @Time.calc_time
    def _init_database(self):
        self.log.info("Initialising database.")
        self.db = Database(self)

    @Time.calc_time
    def _init_plugins(self):
        self.log.info("Initialising plugins.")
        self.plugins = PluginHandler(self)
        self.plugins.load_all()    # Here since Plugin requires self.bot.plugins to load itself.

    def run(self):
        try:
            super().run(self.configs.discord.token)
        except discord.LoginFailure:
            self.log.error("Invalid token provided.")
            raise discord.LoginFailure

    async def on_ready(self):
        self.log.info(f"{self.user.name}#{self.user.discriminator} Ready! [{self.time.round_time()} seconds.]")
        self.log.info(f"User Id: {self.user.id}")
        self.log.info("-------")
