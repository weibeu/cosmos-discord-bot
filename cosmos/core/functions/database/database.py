from motor.motor_asyncio import AsyncIOMotorClient


class Database(AsyncIOMotorClient):

    def __init__(self, bot):
        self.bot = bot
        super().__init__(self.bot.configs.db.uri)
