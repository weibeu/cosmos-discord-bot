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

import discord

from ... import exceptions
from discord.ext import commands

from .checks import CosmosChecks
from .commands import cosmos_command, cosmos_group_command


class FakeGlobalGuildChannel(discord.Object):

    ...


class Cog(commands.Cog, metaclass=commands.CogMeta):

    # TODO: Add load kwarg to determine if cog is to be loaded into plugin.

    # Some shorthands
    command = cosmos_command
    group = cosmos_group_command
    checks = CosmosChecks
    cooldown = commands.cooldown
    bucket_type = commands.BucketType

    FUNCTION = "plugins"
    INESCAPABLE = True    # Determines if cog can be disabled by guild admins.
    # TODO: Handle cog listeners.
    FakeGlobalGuildChannel = FakeGlobalGuildChannel

    def __init__(self, *args, **kwargs):
        # TODO: Improve this.
        self.name = self.__class__.__name__
        self.display_name = None
        self.__get_display_name()
        self._plugin = None
        self._bot = None
        if not self.INESCAPABLE:
            self.disabled_channels = set()

    async def cog_check(self, ctx):
        if not ctx.guild:
            return True
        if not self.INESCAPABLE:
            if FakeGlobalGuildChannel(ctx.guild.id) in self.disabled_channels:
                raise exceptions.DisabledFunctionError(globally=True)
            if ctx.channel in self.disabled_channels:
                raise exceptions.DisabledFunctionError
        return True

    def __get_display_name(self):
        self.display_name = self.name[0]
        for _ in self.name[1:]:
            if _.isupper():
                self.display_name += " "
            self.display_name += _

    @property
    def plugin(self):
        return self._plugin

    @plugin.setter
    def plugin(self, plugin):
        self._plugin = plugin
        self._bot = self._plugin.bot

    @property
    def bot(self):
        return self._bot

    @bot.setter
    def bot(self, bot):
        self._bot = bot

    def _load(self):
        plugin = self.plugin
        plugin.bot.log.info(f"Loading COG {self.__class__.__name__}.")
        cog = self.__class__(plugin)
        if cog.name in plugin.cogs:
            plugin.bot.log.error(f"Cog {self.__class__.__name__} is already loaded.")
            return
        else:
            plugin.bot.add_cog(cog)
            self.plugin.cogs.update({cog.name: cog})
        plugin.bot.log.info("Done.")

    def unload(self):
        self.bot.log.info(f"Unloading COG {self.name}.")
        if self.name not in self.plugin.cogs:
            self.bot.log.error(f"Cog {self.name} is not loaded.")
            return
        else:
            self.bot.remove_cog(self.name)
            self.plugin.cogs.pop(self.name)
        self.bot.log.info(f"COG {self.name} unloaded.")

    def reload(self):
        self.bot.log.info(f"Reloading COG {self.name}.")
        self.unload()
        self._load()
        self.bot.log.info(f"COG {self.name} reloaded.")
