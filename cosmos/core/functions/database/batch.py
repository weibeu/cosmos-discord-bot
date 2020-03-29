from typing import Union

from pymongo.errors import InvalidOperation
from pymongo import InsertOne, UpdateOne, ReplaceOne, DeleteOne


class DatabaseBatch(object):

    def __init__(self, bot, collection):
        self.bot = bot
        self.batch = []
        self.collection = collection

    def queue(self, write_operation: Union[InsertOne, UpdateOne, ReplaceOne, DeleteOne]):
        self.batch.append(write_operation)

    def queue_insert(self, insert_document):
        self.batch.append(InsertOne(insert_document))

    def queue_update(self, filter_document, update_document, *args, **kwargs):
        self.batch.append(UpdateOne(filter_document, update_document, *args, **kwargs))

    def queue_replace(self, filter_document, update_document, *args, **kwargs):
        self.batch.append(ReplaceOne(filter_document, update_document, *args, **kwargs))

    def queue_delete(self, filter_document, collation=None):
        self.batch.append(DeleteOne(filter_document, collation=collation))

    async def write(self, **kwargs):
        if self.batch:
            try:
                self.bot.log.debug(f"Writing [{self.collection.name}] batch updates.")
                result = await self.collection.bulk_write(self.batch, **kwargs)
            except InvalidOperation:
                self.bot.eh.sentry.capture_exception()
            else:
                self.bot.log.debug(f"- Done. [{self.collection.name}] {result.bulk_api_result}.")
                self.batch = list()
        else:
            self.bot.log.debug(f"[{self.collection.name}] batch is empty.")
