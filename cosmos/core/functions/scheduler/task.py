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

import bson
import arrow
import asyncio
import datetime


class ScheduledTask(object):

    def __init__(self, scheduler, callback, invoke_at, kwargs, created_at=None, _id=None, **_kwargs):
        self.id = _id or bson.ObjectId()
        self.scheduler = scheduler
        self.callback = callback
        self.invoke_at = invoke_at
        self.created_at = created_at or datetime.datetime.utcnow()
        self.kwargs = kwargs

        if self.invoke_at <= self.created_at:
            raise ValueError("The task must be scheduled to future.")

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.id == other.id

    def __call__(self, *args, **kwargs):
        if self.callback.startswith("on_"):
            self.scheduler.bot.dispatch(self.callback, self, *args, **kwargs, **self.kwargs)
        else:
            try:
                object_ = self.scheduler.callbacks[self.callback]
            except KeyError:
                raise ValueError(f"No callback '{self.callback}' is registered yet.")
            else:
                self.scheduler.bot.loop.create_task(object_(self, *args, **kwargs, **self.kwargs))

        self.scheduler.bot.loop.create_task(self.scheduler.remove_task(self))

    async def __dispatch_when_ready(self, *args, **kwargs):
        await asyncio.sleep(self.delta.total_seconds())
        self.__call__(*args, **kwargs)

    def dispatch_when_ready(self, *args, **kwargs):
        self.scheduler.bot.loop.create_task(self.__dispatch_when_ready(*args, **kwargs))

    @property
    def document(self):
        return {
            "_id": self.id, "callback": self.callback, "invoke_at": self.invoke_at,
            "created_at": self.created_at, "kwargs": dict(self.kwargs),
        }

    @classmethod
    def from_document(cls, scheduler, document):
        return cls(scheduler, **document)

    @property
    def life(self):
        return self.invoke_at - self.created_at

    @property
    def delta(self):
        return self.invoke_at - datetime.datetime.utcnow()

    @property
    def humanize(self):
        return arrow.get(self.invoke_at).humanize()
