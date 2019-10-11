from abc import ABC

from discord import Color
from .base import CosmosGuildBase

from ...moderation.models import automoderation


class WelcomeBannerSettings(CosmosGuildBase, ABC):

    def __init__(self, **kwargs):
        raw_welcome_settings = kwargs.get("welcome", dict())
        raw_banner_settings = raw_welcome_settings.get("banner", dict())
        self.welcome_banner_url = raw_banner_settings.get("url", str())
        self.welcome_banner_text = raw_banner_settings.get("text", str())
        self.__welcome_banner_channel_id = raw_banner_settings.get("channel", int())
        self.welcome_banner_enabled = raw_banner_settings.get("enabled", False)

    @property
    def welcome_banner_channel(self):
        return self.guild.get_channel(self.__welcome_banner_channel_id)

    async def set_welcome_banner(self, banner_url, text, channel_id):
        self.welcome_banner_url = banner_url
        self.welcome_banner_text = text
        self.__welcome_banner_channel_id = channel_id
        self.welcome_banner_enabled = False

        await self.collection.update_one(
            self.document_filter, {"$set": {
                "settings.welcome.banner.url": self.welcome_banner_url,
                "settings.welcome.banner.text": self.welcome_banner_text,
                "settings.welcome.banner.channel": self.__welcome_banner_channel_id,
                "settings.welcome.banner.enabled": self.welcome_banner_enabled
            }}
        )

    async def enable_welcome_banner(self, enable=True):
        self.welcome_banner_enabled = enable

        await self.collection.update_one(self.document_filter, {"$set": {"settings.welcome.banner.enabled": enable}})

# TODO: Don't pass whole document. Rather pass the embedded document of only that model to remove raw_..._settings.


class ThemeSettings(object):

    def __init__(self, guild_profile, **kwargs):
        self.__profile = guild_profile
        raw_theme_settings = kwargs.get("theme", dict())
        color = raw_theme_settings.get("color")
        if color is not None:
            self.color = Color(color)
        else:
            self.color = None

    async def set_color(self, color):
        self.color = color

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$set": {"settings.theme.color": self.color.value}}
        )

    async def remove_color(self):
        self.color = None

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$unset": {"settings.theme.color": ""}}
        )


class GuildLogger(object):

    def __init__(self, name, channel):
        self.name = name
        self.channel = channel

    @property
    def document(self):
        return {
            "name": self.name,
            "channel": self.channel.id,
        }


class LoggerSettings(CosmosGuildBase, ABC):

    def __init__(self, **kwargs):
        raw_logger_settings = kwargs.get("loggers", list())
        self.loggers = self.__get_loggers(raw_logger_settings)

    def __get_loggers(self, raw_settings):
        return [GuildLogger(_["name"], self.guild.get_channel(_["channel"])) for _ in raw_settings]

    def get_logger(self, name):
        for logger in self.loggers:
            if logger.name == name:
                return logger

    async def enable_logger(self, name, channel):
        logger = GuildLogger(name, channel)
        self.loggers.append(logger)

        await self.collection.update_one(
            self.document_filter, {"$pull": {"settings.loggers": {"name": logger.name}}}
        )

        await self.collection.update_one(
            self.document_filter, {"$addToSet": {"settings.loggers": logger.document}}
        )

    async def remove_logger(self, name):
        for logger in self.loggers:
            if logger.name == name:
                self.loggers.remove(logger)

        await self.collection.update_one(
            self.document_filter, {"$pull": {"settings.loggers": {"name": name}}}
        )


class AutoModerationSettings(object):

    def __init__(self, guild_profile, **kwargs):
        self.__profile = guild_profile
        _settings = kwargs.get("auto_moderation", dict())
        self.triggers = self.__get_triggers(_settings.get("triggers", list()))
        self.auto_mute_timer = _settings.get("auto_mute_timer", 0)

    def __get_triggers(self, raw_triggers):
        return {_["name"]: automoderation.AutoModerationTrigger(self.__profile, **_) for _ in raw_triggers}

    async def create_trigger(self, trigger_name, actions):
        trigger = automoderation.AutoModerationTrigger(
            self.__profile, name=trigger_name, actions=actions,
        )
        self.triggers[trigger_name] = trigger

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {"settings.auto_moderation.triggers": {"name": trigger.name}}}
        )    # Remove if trigger already exists.

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$addToSet": {
                "settings.auto_moderation.triggers": trigger.document
            }}
        )

    async def remove_trigger(self, trigger_name):
        self.triggers.pop(trigger_name)

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {
                "settings.auto_moderation.triggers": {"name": trigger_name}
            }}
        )

    async def ban_word(self, word):
        trigger = self.triggers["banned_words"]
        try:
            trigger.words.add(word)
        except AttributeError:
            trigger.words = {word, }

        document_filter = self.__profile.document_filter.copy()
        document_filter.update({"settings.auto_moderation.triggers.name": trigger.name})

        await self.__profile.collection.update_one(
            document_filter, {"$addToSet": {"settings.auto_moderation.triggers.$.words": word}}
        )

    async def clear_banned_words(self):
        trigger = self.triggers["banned_words"]
        trigger.words.clear()

        document_filter = self.__profile.document_filter.copy()
        document_filter.update({"settings.auto_moderation.triggers.name": trigger.name})

        await self.__profile.collection.update_one(
            document_filter, {"$unset": {"settings.auto_moderation.triggers.$.words": ""}}
        )

    async def set_auto_mute_timer(self, minutes):
        self.auto_mute_timer = minutes
        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$set": {"settings.auto_moderation.auto_mute_timer": minutes}})

    def has_trigger(self, trigger):
        return trigger in self.triggers


class Reactor(object):

    def __init__(self, channel, emotes, enabled):
        self.channel = channel
        self.emotes = emotes
        self.enabled = enabled

    @property
    def document(self):
        return {
            "channel_id": self.channel.id,
            "emotes": [_.id for _ in self.emotes],
            "enabled": self.enabled,
        }


class ReactorSettings(object):

    def __init__(self, guild_profile, documents):
        self.__profile = guild_profile
        self.reactors = [Reactor(
            self.__profile.guild.get_channel(_["channel_id"]), [
                self.__profile.plugin.bot.get_emoji(_id) for _id in _["emotes"]
            ], _["enabled"]
        ) for _ in documents]

    def __bool__(self):
        return bool(self.reactors)

    def get_reactor(self, channel_id):
        try:
            return [reactor for reactor in self.reactors if reactor.channel.id == channel_id][0]
        except IndexError:
            pass

    def __remove_reactor(self, channel_id):
        reactor = self.get_reactor(channel_id)
        if reactor:
            self.reactors.remove(reactor)

    async def set_reactor(self, channel, emotes):
        if self.get_reactor(channel.id):
            self.__remove_reactor(channel.id)    # Replace with new reactor if a reactor already exists in that channel.
        reactor = Reactor(channel, emotes, True)

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$addToSet": {f"settings.reactor": {reactor.document}}}
        )

    async def remove_reactor(self, channel):
        self.__remove_reactor(channel.id)

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {f"settings.reactor": {"channel_id": channel.id}}}
        )

    async def enable_reactor(self, reactor, enabled=True):
        reactor.enabled = enabled

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {f"settings.reactor": {"channel_id": reactor.channel.id}}}
        )
        self.__profile.collection.update_one(
            self.__profile.document_filter, {"$addToSet": {"settings.reactor": {reactor.document}}}
        )


class GuildSettings(WelcomeBannerSettings, LoggerSettings, ABC):

    def __init__(self, **kwargs):
        raw_settings = kwargs.get("settings", dict())
        WelcomeBannerSettings.__init__(self, **raw_settings)
        LoggerSettings.__init__(self, **raw_settings)
        self.auto_moderation = AutoModerationSettings(self, **raw_settings)
        self.theme = ThemeSettings(self, **raw_settings)
        self.reactors = ReactorSettings(self, raw_settings.get("reactors", dict()))
        self.moderators = raw_settings.get("moderators", list())
        self.presets = raw_settings.get("presets", dict())
        self.roles = raw_settings.get("roles", dict())

    async def add_moderator(self, _id):
        self.moderators.append(_id)

        await self.collection.update_one(
            self.document_filter, {"$addToSet": {"settings.moderators": _id}}
        )

    async def remove_moderator(self, _id):
        self.moderators.remove(_id)

        await self.collection.update_one(
            self.document_filter, {"$pull": {"settings.moderators": _id}}
        )

    async def set_preset(self, command_name, **kwargs):
        self.presets[command_name] = kwargs

        await self.collection.update_one(
            self.document_filter, {"$set": {f"settings.presets.{command_name}": kwargs}}
        )

    async def remove_preset(self, command_name):
        self.presets.pop(command_name)

        await self.collection.update_one(
            self.document_filter, {"$unset": {f"settings.presets.{command_name}": ""}}
        )

    async def set_role(self, role_for, role_id=None, **document):
        self.roles[role_for] = role_id or document

        await self.collection.update_one(
            self.document_filter, {"$set": {f"settings.roles.{role_for}": role_id or document}}
        )

    async def remove_role(self, role_for):
        self.roles.pop(role_for)

        await self.collection.update_one(
            self.document_filter, {"$unset": {f"settings.roles.{role_for}": ""}}
        )
