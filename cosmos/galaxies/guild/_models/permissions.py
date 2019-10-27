from abc import ABC

from .base import CosmosGuildBase


class DisabledFunctions(object):

    def __init__(self, bot, document):
        self.__bot = bot
        self.__fetch_commands(document.get("commands", list()))

    def __get_channels(self, channel_ids):
        return [self.__bot.get_channel(_) for _ in channel_ids]

    def __fetch_commands(self, _documents):
        for command_name, channel_ids in _documents:
            command = self.__bot.get_command(command_name)
            try:
                command.disabled_channels.extend(self.__get_channels(channel_ids))
            except AttributeError:
                pass    # Command is inescapable.
            # Dynamically patch channels to which commands are meant to be disabled.
            # command.disabled_channels = [self.__bot.get_channel(_) for _ in channel_ids]
            # Rather than dynamically patching, make commands use custom cls with disabled_channels
            # as one of its attributes and append channels to it.

    def __fetch_plugins(self, _document):    # Actually cogs.
        for plugin_name, channel_ids in _document.items():
            plugin = self.__bot.get_cog(plugin_name)
            try:
                plugin.disabled_channels.extend(self.__get_channels(channel_ids))
            except AttributeError:
                pass    # Cog is inescapable.

    @staticmethod
    def __get(_disabled, name):
        try:
            return [_ for _ in _disabled if _.name.lower() == name.lower()][0]
        except IndexError:
            pass

    def get(self, mode, name):
        return self.__get(self[mode], name)

    def get_command(self, name):
        return self.__get(self.commands, name)

    def get_plugin(self, name):
        return self.__get(self.plugins, name)

    def get_galaxy(self, name):
        return self.__get(self.galaxies, name)

    def __getitem__(self, item):    # -> _disabled
        return self.__getattribute__(item)


class GuildPermissions(CosmosGuildBase, ABC):

    def __init__(self, document):
        # self.disabled_commands = []    # mode = "commands"
        # self.disabled_plugins = []     # mode = "plugins"
        # self.disabled_galaxies = []    # mode = "galaxies"
        # Generalisation of above three attributes are represented using '_disabled'.
        self.disabled = DisabledFunctions(self.plugin.bot, document.get("disabled", dict()))

    @staticmethod
    def __get(_disabled, name):
        try:
            return [_ for _ in _disabled if _.name.lower() == name.lower()][0]
        except IndexError:
            pass

    def __get_disabled(self, mode):
        return getattr(self.disabled, mode)

    async def __disable(self, mode, name, channels=None):
        _disabled = self.__get_disabled(mode)
        if _ := self.__get(_disabled, name):
            _disabled.remove(_)

        _ = [_ for _ in _disabled if _.name.lower() == name.lower()][0]    # Particular command, plugin or galaxy.
        _disabled.append(_)    # Add direct reference to _ rather than just str name for a reason.

        await self.collection.update_one(
            self.document_filter, {"$pull": {f"settings.permissions.disabled.{mode}": {"name": _.name}}}
        )    # For cases when old document is not same as new document ensuring 'name' as primary key.
        await self.collection.update_one(
            self.document_filter, {"$addToSet": {f"settings.permissions.disabled.{mode}": {
                "name": _.name,
                "channels": [_.id for _ in channels],
            }}}
        )

    async def __enable(self, mode, name, channel=None):
        _disabled = self.__get_disabled(mode)
        _ = self.__get(_disabled, name)
        if channel and channel in _.disabled_channels:
            _.disabled_channels.remove(channel)
            document_filter = self.document_filter.copy()
            document_filter.update({f"settings.permissions.disabled.{mode}.name": name})
            await self.collection.update_one(
                document_filter, {"$pull": {f"settings.permissions.disabled.{mode}.$.channels": channel.id}}
            )

        _disabled.remove(_)
        await self.collection.update_one(
            self.document_filter, {"$pull": {f"settings.permissions.disabled.{mode}": {"name": name}}}
        )
