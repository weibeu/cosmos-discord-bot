from discord import LoginFailure

from .tasks import InitialTasks
from .functions import CosmosContext


class Cosmos(InitialTasks):

    def __init__(self):
        self.time = None
        self.configs = None
        self.eh = None
        self.log = None
        self.cache = None
        self.db_client = None
        self.db = None
        self.emotes = None
        self.plugins = None
        self.theme = None
        super().__init__()

    async def get_context(self, message, *, context_class=CosmosContext):
        return await super().get_context(message, cls=context_class)

    def run(self):
        try:
            super().run(self.configs.discord.token)
        except LoginFailure:
            self.log.error("Invalid token provided.")
            raise LoginFailure

    async def on_ready(self):
        self.log.info(f"{self.user.name}#{self.user.discriminator} Ready! [{self.time.round_time()} seconds.]")
        self.log.info(f"User Id: {self.user.id}")
        self.log.info("------------------------")
