from discord import LoginFailure

from .tasks import InitialTasks
from .functions import CosmosContext


class Cosmos(InitialTasks):

    async def get_context(self, message, *, context_class=CosmosContext):
        return await super().get_context(message, cls=context_class)

    def run(self):
        try:
            super().run(self.configs.discord.token)
        except LoginFailure:
            self.log.error("Invalid token provided.")
            raise LoginFailure

    def get_galaxy(self, name):
        return self.plugins.get(display_name=name)

    async def on_ready(self):
        self.log.info(f"{self.user.name}#{self.user.discriminator} Ready! [{self.time.round_time()} seconds.]")
        self.log.info(f"User Id: {self.user.id}")
        self.log.info("------------------------")
