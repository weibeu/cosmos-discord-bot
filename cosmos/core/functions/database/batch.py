"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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
