import discord

from discord.ext import commands
from cosmos.core.utilities.time import Time
from cosmos.core.functions.configs.handler import ConfigHandler
from cosmos.core.functions.logger.handler import LoggerHandler
from cosmos.core.functions.plugins.handler import PluginHandler


class Cosmos(commands.Bot):

    def __init__(self, token=None, client_id=None, prefixes=None):
        self.time = None
        self.configs = None
        self.plugins = None
        self.logger = None
        self._init_time()
        self._init_configs()
        self._init_logger()
        self._init_plugins()
        self.configs.discord.token = token or self.configs.discord.token
        self.configs.discord.client_id = client_id or self.configs.discord.client_id
        self.configs.discord.prefixes = prefixes or self.configs.cosmos.prefixes
        super().__init__(command_prefix=commands.when_mentioned_or(*self.configs.cosmos.prefixes))

    def _init_time(self):
        self.time = Time()

    def _init_configs(self):
        self.configs = ConfigHandler()

    def _init_logger(self):
        self.logger = LoggerHandler(self)

    def _init_plugins(self):
        self.plugins = PluginHandler(self)

    def run(self):
        try:
            super().run(self.configs.discord.token)
        except discord.LoginFailure:
            print("Invalid token provided.")

    async def on_ready(self):
        print(f"{self.user.name}#{self.user.discriminator} Ready!")
        print(f"User Id: {self.user.id}")
        print("-------")
