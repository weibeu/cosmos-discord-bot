from discord.ext import tasks
from .task import ScheduledTask


class Scheduler(object):

    def __init__(self, bot):
        self.bot = bot
        self.collection = self.bot.db[self.bot.configs.scheduler.collection]
        self.tasks = []
        self.callbacks = {}
        self.bot.loop.create_task(self.__fetch_tasks())

    def register_callback(self, object_):
        if not callable(object_):
            raise ValueError("Provided callback object is not callable.")
        if object_.__name__.startswith("on_"):
            raise ValueError("Callback name shouldn't start with 'on_'.")
        self.callbacks[object_.__name__] = object_

    async def __fetch_tasks(self):
        self.tasks = [ScheduledTask.from_document(self, document) for document in await self.collection.find(
            {"invoke_at": {"$lt": self.bot.configs.scheduler.passive_after}}
        ).to_list(None)]
        await self.initialize_tasks()

    async def initialize_tasks(self):
        for task in self.tasks:
            await task.dispatch_when_ready()

    async def schedule(self, callback, to, **kwargs):
        task = ScheduledTask(self, callback, to, kwargs)

        if task.timedelta.seconds < self.bot.configs.scheduler.persist_at:
            return await task.dispatch_when_ready()

        await self.collection.insert_one(task.document)

        if task.invoke_at <= self.bot.configs.scheduler.passive_after:
            self.tasks.append(task)

        return task

    async def remove(self, task):
        try:
            self.tasks.remove(task)
        except ValueError:
            pass
        if task.timedelta.seconds <= self.bot.configs.scheduler.persist_at:
            return

        await self.collection.delete_one({"_id": task.id})

    async def fetch_task(self, **kwargs):
        ...
