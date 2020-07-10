from ...core.utilities import converters

import datetime
import discord

from .. import Cog, UserNotPrime
from discord.ext import commands


class _PastTimeError(commands.BadArgument):

    handled = True


class ReminderTimeConverter(converters.HumanDatetimeConverter):

    async def convert(self, ctx, argument):
        mixin = await super().convert(ctx, argument)
        if mixin.datetime < datetime.datetime.utcnow():
            raise _PastTimeError
        return mixin


class Reminder(Cog):
    """Reminder which reminds you of something in distant future."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.bot.scheduler.register_callback(self.__remind)

    async def get_reminders(self, user_id):
        return await self.bot.scheduler.fetch_tasks(user_id=user_id)

    async def __remind(self, task, user_id, channel_id, message):
        try:
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
        except discord.NotFound:
            return
        period = "." if not message.endswith(".") else str()
        await channel.send(f"{user.mention} {message}{period}")

    @Cog.group(name="reminder", aliases=["remind", "timer", "remindme"], invoke_without_command=True)
    async def reminder(self, ctx, *, when: ReminderTimeConverter):
        """Set reminder to get notified at specified time in future in the same channel in which you
        created the reminder.

        You can specify when in number of formats. To include a message with reminder, just include it
        after you specify the when parameter.

        To set your reminder with a time difference, begin with 'in '. Otherwise normally specify the date
        and time you want to set reminder to.

        """
        profile = await ctx.fetch_cosmos_user_profile()
        reminders = await self.get_reminders(ctx.author.id)
        if len(reminders) >= self.plugin.data.reminders.max_reminders and not profile.is_prime:
            raise UserNotPrime("Click to get prime to create infinite reminders with all other features.")
        task = await self.bot.scheduler.schedule(
            "__remind", when.datetime, message=when.message, user_id=ctx.author.id, channel_id=ctx.channel.id)
        await ctx.send_line(f"✅    Your reminder is set to trigger {task.humanize}.")

    @reminder.error
    async def reminder_error(self, ctx, error):
        if isinstance(error, _PastTimeError):
            return await ctx.send_line(f"❌    You can't set reminders in past because it has already expired.")
