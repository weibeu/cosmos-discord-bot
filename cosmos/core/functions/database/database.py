from motor.motor_asyncio import AsyncIOMotorClient

from .batch import DatabaseBatch


class DatabaseClient(AsyncIOMotorClient):

    def __init__(self, bot):
        self.bot = bot
        self.uri = self.bot.configs.db.uri
        self.database_name = self.bot.configs.db.database
        super().__init__(self.uri)
        self.db = self.get_database()

    def get_database(self, database_name: str = None):
        name = self.database_name or database_name
        database = self[name]
        return database

    def batch(self, collection):
        return DatabaseBatch(self.bot, collection)
