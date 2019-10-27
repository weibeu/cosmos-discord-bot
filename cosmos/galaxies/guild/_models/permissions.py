from abc import ABC

from .base import CosmosGuildBase


class DisabledFunctions(object):

    def __init__(self, bot, document):
        self.__bot = bot
        self.__fetch_commands(document.get("commands", dict()))    # {command_name: [channel_ids], }
        self.__fetch_plugins(document.get("plugins", dict()))

    def __get_channels(self, channel_ids):
        return [self.__bot.get_channel(_) for _ in channel_ids]

    def __fetch_commands(self, _documents):    # mode = "command"
        for command_name, channel_ids in _documents.items():
            command = self.get("command", command_name)
            try:
                command.disabled_channels.update(self.__get_channels(channel_ids))
            except AttributeError:
                pass    # Command is inescapable.
            # Dynamically patch channels to which commands are meant to be disabled.
            # command.disabled_channels = [self.__bot.get_channel(_) for _ in channel_ids]
            # Rather than dynamically patching, make commands use custom cls with disabled_channels
            # as one of its attributes and append channels to it.

    def __fetch_plugins(self, _document):    # mode = "cog"
        for plugin_name, channel_ids in _document.items():
            plugin = self.get("cog", plugin_name)
            try:
                plugin.disabled_channels.update(self.__get_channels(channel_ids))
            except AttributeError:
                pass    # Cog is inescapable.

    def get(self, mode, name):
        if mode == "commands":
            return self.__bot.get_command(name)
        elif mode == "plugins":
            return self.__bot.get_cog(name)
        elif mode == "galaxies":
            return    # TODO: Implement get_galaxy method.
        else:
            raise NameError


class GuildPermissions(CosmosGuildBase, ABC):

    def __init__(self, document):
        # self.disabled_commands = []    # mode = "commands"
        # self.disabled_plugins = []     # mode = "plugins"
        # self.disabled_galaxies = []    # mode = "galaxies"
        # Generalisation of above three attributes are represented using '_disabled'.
        self.disabled = DisabledFunctions(self.plugin.bot, document.get("disabled", dict()))

    async def __disable(self, mode, name, channels):
        _ = self.disabled.get(mode, name)
        _.disabled_channels.update(channels)

        await self.collection.update_one(self.document_filter, {
            "$addToSet": {f"settings.permissions.disabled.{mode}.{name}": {"$each": [_.id for _ in channels]}}
        })

    async def __enable(self, mode, name, channels):
        _ = self.disabled.get(name, mode)
        _.disabled_channels.difference_update(channels)

        await self.collection.update_one(self.document_filter, {
            "$pull": {f"settings.permissions.disabled.{mode}.{name}": {"$each": [_.id for _ in channels]}}
        })
