import discord

from discord.ext import commands
from cosmos.core.configs.config import Config


class Cosmos(commands.Bot):

    def __init__(self, token=None, client_id=None, prefixes=None):
        self.configs = None
        self._init_configs()
        if token is not None:
            self.configs.discord.token = token
        if client_id is not None:
            self.configs.discord.client_id = client_id
        if prefixes is not None:
            self.configs.discord.prefixes = prefixes
        super().__init__(command_prefix=commands.when_mentioned_or(*self.configs.cosmos.prefixes))

    def _init_configs(self):
        self.configs = Config()

    def run(self):
        try:
            super().run(self.configs.discord.token)
        except discord.LoginFailure:
            print("Invalid token provided.")

    async def on_ready(self):
        print(f"{self.user.name}#{self.user.discriminator} Ready!")
        print(f"User Id: {self.user.id}")
        print("-------")
