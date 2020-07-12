from discord.ext import tasks
from .task import ScheduledTask


class Scheduler(object):

    REFRESH_TASKS_AT = 24

    def __init__(self, bot):
        self.bot = bot
        self.collection = self.bot.db[self.bot.configs.scheduler.collection]
        self.tasks = set()
        self.callbacks = {}
        self.bot.loop.create_task(self.__fetch_tasks())

    def register_callback(self, object_, name=None):
        name = name or object_.__name__
        if not callable(object_):
            raise ValueError("Provided callback object is not callable.")
        if name.startswith("on_"):
            raise ValueError("Callback name shouldn't start with 'on_'.")
        if name in self.callbacks:
            raise TypeError("Callback with such name is already registered.")
        self.callbacks[name] = object_

    async def __fetch_tasks(self):
        self.tasks = {ScheduledTask.from_document(self, document) for document in await self.collection.find(
            {"invoke_at": {"$lt": self.bot.configs.scheduler.passive_after}}
        ).to_list(None)}
        self.initialize_tasks()

    @tasks.loop(hours=REFRESH_TASKS_AT)
    async def refresh_tasks(self):
        await self.__fetch_tasks()

    def initialize_tasks(self):
        for task in self.tasks:
            task.dispatch_when_ready()

    async def schedule(self, callback, to, **kwargs):
        # if not isinstance(callback, str):
        #     try:
        #         self.register_callback(callback)
        #     except TypeError:
        #         pass
        #     callback = callback.__name__

        task = ScheduledTask(self, callback, to, kwargs)

        if task.life.seconds < self.bot.configs.scheduler.persist_at:
            task.dispatch_when_ready()
            return task

        await self.collection.insert_one(task.document)

        if task.invoke_at <= self.bot.configs.scheduler.passive_after:
            self.tasks.add(task)

        return task

    async def remove_task(self, task):
        try:
            self.tasks.remove(task)
        except KeyError:
            pass
        if task.life.seconds < self.bot.configs.scheduler.persist_at:
            return

        await self.collection.delete_one({"_id": task.id})

    def get_tasks(self, **kwargs):
        tasks_ = set()
        for t in self.tasks:
            # if len(set(task.kwargs.keys()) & set(kwargs.keys())) == len(kwargs):
            try:
                if all([t.kwargs[k] == v for k, v in kwargs.items()]):
                    tasks_.add(t)
            except KeyError:
                pass
        return tasks_

    async def fetch_tasks(self, **kwargs):
        tasks_ = {ScheduledTask.from_document(self, document) for document in await self.collection.find(
            {f"kwargs.{k}": v for k, v in kwargs.items()}
        ).to_list(None)}
        tasks_.update({
            t for t in self.get_tasks(**kwargs) if t.life.seconds <= self.bot.configs.scheduler.persist_at
        })
        tasks_ = list(tasks_)
        tasks_.sort(key=lambda t: t.invoke_at)
        return tasks_
