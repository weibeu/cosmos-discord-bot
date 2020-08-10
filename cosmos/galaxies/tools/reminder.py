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

from ...core.utilities import converters

import bson
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


class ReminderIDConverter(commands.Converter):

    async def convert(self, ctx, argument):
        try:
            return bson.ObjectId(argument)
        except bson.errors.InvalidId:
            raise commands.BadArgument


class Reminder(Cog):
    """Reminder which reminds you of something in distant future."""

    INESCAPABLE = False

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
        self.bot.scheduler.register_callback(self.__remind)

    async def get_reminders(self, user_id):
        return list(await self.bot.scheduler.fetch_tasks(self.__remind, user_id=user_id))

    async def __remind(self, task, user_id, channel_id, message):
        try:
            channel = self.bot.get_channel(channel_id) or await self.bot.fetch_channel(channel_id)
            user = self.bot.get_user(user_id) or await self.bot.fetch_user(user_id)
        except discord.NotFound:
            return
        period = "." if not message.endswith(".") else str()
        if message:
            embed = self.bot.theme.embeds.primary()
            embed.description = f"{message}{period}"
            embed.timestamp = datetime.datetime.utcnow()
            embed.set_footer(text=task.id, icon_url=user.avatar_url)
            embed.set_author(name="!! Reminder", icon_url=self.bot.theme.images.reminder)
        else:
            embed = self.bot.theme.embeds.one_line.primary(
                "!! Your reminder has been triggered.", self.bot.theme.images.reminder)
        await channel.send(content=user.mention, embed=embed)

    @Cog.group(name="reminder", aliases=["remind", "timer", "remindme", "alarm"], invoke_without_command=True)
    async def reminder(self, ctx, *, when: ReminderTimeConverter = None):
        """Set reminder to get notified at specified time in future in the same channel in which you
        created the reminder.

        You can specify when in number of formats. To include a message with reminder, just include it
        after you specify the when parameter.

        To set your reminder with a time difference, begin with 'in '. Otherwise normally specify the date
        and time you want to set reminder to. However this is not necessary anymore.

        Note: Reminders smaller than 60 seconds will not be persisted. Meaning if the bot restarts or the universe
        explodes and resets during this duration then, such reminders will not be triggered.

        """
        if not when:
            return await self.reminders(ctx)
        profile = await ctx.fetch_cosmos_user_profile()
        reminders = await self.get_reminders(ctx.author.id)
        if len(reminders) >= self.plugin.data.reminders.max_reminders and not profile.is_prime:
            raise UserNotPrime("Click to get prime to create infinite reminders with all other features.")
        if when.delta.days >= self.plugin.data.reminders.max_life and not profile.is_prime:
            raise UserNotPrime("Get prime to schedule reminder beyond age of universe and other features.")
        task = await self.bot.scheduler.schedule(
            "__remind", when.datetime, message=when.message, user_id=ctx.author.id, channel_id=ctx.channel.id)
        await ctx.send_line(f"✅    Your reminder has been set and will trigger {task.humanize}.")

    @reminder.command(name="remove", aliases=["delete"])
    async def remove_reminder(self, ctx, reminder_id: ReminderIDConverter):
        """Removes the reminder with specified reminder ID. You can get the reminder ID from ;reminders command."""
        reminders = await self.get_reminders(ctx.author.id)
        if not reminders:
            return await ctx.send_line("❌    You haven't created any reminders yet.")
        try:
            reminder = [r for r in reminders if r.id == reminder_id][0]
        except IndexError:
            return await ctx.send_line("❌    Didn't found any reminder with provided reminder ID.")
        await self.bot.scheduler.remove_task(reminder)
        await ctx.send_line("✅    Specified reminder has been removed from your reminders list.")

    # TODO: Remove all reminders command.

    @reminder.error
    async def reminder_error(self, ctx, error):
        if isinstance(error, _PastTimeError):
            return await ctx.send_line(f"❌    You can't set reminders in past because it has already expired.")

    async def __reminders_entry_parser(self, _ctx, task, tasks):
        try:
            bullet = getattr(self.bot.emotes.misc, self.plugin.data.reminders.bullets[tasks.index(task)])
        except IndexError:
            bullet = self.bot.emotes.misc.asterisk
        key = f"{bullet}    {task.humanize} ..."
        value = f'**Location**: <#{task.kwargs["channel_id"]}>\n' \
                f'**ID**: `{task.id}`'
        if task.kwargs["message"]:
            value = f'*{task.kwargs["message"].strip()}*\n' + value
        return key, value

    @Cog.group(name="reminders", invoke_without_command=True)
    async def reminders(self, ctx):
        """Displays list of reminders which has been created by you."""
        reminders = await self.get_reminders(ctx.author.id)
        if not reminders:
            return await ctx.send_line("❌    You haven't created any reminders yet.")
        paginator = ctx.get_field_paginator(reminders, 7, entry_parser=self.__reminders_entry_parser, inline=False)
        paginator.embed.set_author(name=f"{ctx.author.name}'s Reminders".upper(), icon_url=ctx.author.avatar_url)
        await paginator.paginate()

    @reminders.command(name="remove", aliases=["delete"])
    async def remove_reminder_(self, ctx, reminder_id: ReminderIDConverter):
        """Removes the reminder with specified reminder ID. You can get the reminder ID from ;reminders command."""
        await self.remove_reminder(ctx, reminder_id)
