from ...moderation.models import automoderation

from abc import ABC
from discord import Color, Embed

from .base import CosmosGuildBase
from .permissions import GuildPermissions


class WelcomeBannerSettings(CosmosGuildBase, ABC):

    def __init__(self, **kwargs):
        self.welcome_banner_url = kwargs.get("url", str())
        self.welcome_banner_text = kwargs.get("text", str())
        self.__welcome_banner_channel_id = kwargs.get("channel", int())
        self.welcome_banner_enabled = kwargs.get("enabled", False)

    @property
    def welcome_banner_channel(self):
        return self.guild.get_channel(self.__welcome_banner_channel_id)

    async def set_welcome_banner(self, banner_url, text, channel_id):
        self.welcome_banner_url = banner_url
        self.welcome_banner_text = text
        self.__welcome_banner_channel_id = channel_id
        self.welcome_banner_enabled = True

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


class WelcomeSettings(WelcomeBannerSettings, ABC):

    def __init__(self, **kwargs):
        raw_welcome_settings = kwargs.get("welcome", dict())
        WelcomeBannerSettings.__init__(self, **raw_welcome_settings.get("banner", dict()))
        self.welcome_message = raw_welcome_settings.get("message", str())
        self.welcome_message_channel = self.plugin.bot.get_channel(raw_welcome_settings.get("message_channel"))
        self.direct_welcome_message = raw_welcome_settings.get("direct_message", str())
        self.welcome_roles = [self.guild.get_role(_id) for _id in raw_welcome_settings.get("roles", list())]

    async def set_welcome_roles(self, roles):
        self.welcome_roles = roles

        await self.collection.update_one(self.document_filter, {
            "$set": {"settings.welcome.roles": [role.id for role in roles]}
        })

    async def remove_welcome_roles(self):
        self.welcome_roles = []

        await self.collection.update_one(self.document_filter, {"$unset": {"settings.welcome.roles": ""}})

    async def set_welcome_message(self, message, channel):
        self.welcome_message = message
        self.welcome_message_channel = channel

        await self.collection.update_one(self.document_filter, {
            "$set": {"settings.welcome.message": message, "settings.welcome.message_channel": channel.id}})

    async def remove_welcome_message(self):
        self.welcome_message = str()
        self.welcome_message_channel = None

        await self.collection.update_one(self.document_filter, {
            "$unset": {"settings.welcome.message": "", "settings.welcome.message_channel": ""}})

    async def set_direct_welcome_message(self, message):
        self.direct_welcome_message = message

        await self.collection.update_one(self.document_filter, {"$set": {"settings.welcome.direct_message": message}})

    async def remove_direct_welcome_message(self):
        self.direct_welcome_message = str()

        await self.collection.update_one(self.document_filter, {"$unset": {"settings.welcome.direct_message": ""}})


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

    def get_embed(self, **kwargs):
        return Embed(color=self.color or self.__profile.plugin.bot.configs.color_scheme.primary, **kwargs)


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
        emotes = []
        for emote in self.emotes:
            if isinstance(emote, str):
                emotes.append(emote)
            else:
                emotes.append(emote.id)
        return {
            "channel_id": self.channel.id,
            "emotes": emotes,
            "enabled": self.enabled,
        }


class ReactorSettings(object):

    def __init__(self, guild_profile, reactors):
        self.__profile = guild_profile
        self.reactors = [Reactor(
            self.__profile.guild.get_channel(_["channel_id"]), [
                self.__profile.plugin.bot.get_emoji(__) or __ for __ in _["emotes"]
            ], _["enabled"]
        ) for _ in reactors]

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
        self.reactors.append(reactor)

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {f"settings.reactors": {"channel_id": reactor.channel.id}}}
        )    # Pull if already exists.
        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$addToSet": {f"settings.reactors": reactor.document}}
        )

    async def remove_reactor(self, channel):
        self.__remove_reactor(channel.id)

        await self.__profile.collection.update_one(
            self.__profile.document_filter, {"$pull": {f"settings.reactors": {"channel_id": channel.id}}}
        )

    async def enable_reactor(self, reactor, enabled=True):
        reactor.enabled = enabled

        document_filter = self.__profile.document_filter.copy()
        document_filter.update({"settings.reactors.channel_id": reactor.channel.id})
        await self.__profile.collection.update_one(
            document_filter, {"$set": {"settings.reactors.$.enabled": reactor.enabled}}
        )


class GuildStarboard(object):

    def __init__(self, channel, count):
        self.channel = channel
        self.count = count


class VerificationSettings(object):

    def __init__(self, guild_profile, **document):
        self.__profile = guild_profile
        self.role = self.__profile.guild.get_role(document.get("role"))
        self.reaction_message_id = document.get("reaction_message")

    async def set_role(self, role):
        self.role = role

        await self.__profile.collection.update_one(self.__profile.document_filter, {"$set": {
            "settings.verification.role": role.id}})

    async def remove_role(self):
        self.role = None

        await self.__profile.collection.update_one(self.__profile.document_filter, {"$unset": {
            "settings.verification.role": ""}})

    async def set_reaction_verification(self, message_id):
        self.reaction_message_id = message_id

        await self.__profile.collection.update_one(self.__profile.document_filter, {"$set": {
            "settings.verification.reaction_message": message_id}})

    async def remove_reaction_verification(self):
        self.reaction_message_id = None

        await self.__profile.collection.update_one(self.__profile.document_filter, {"$unset": {
            "settings.verification.reaction_message": ""}})


class GuildSettings(WelcomeSettings, LoggerSettings, GuildPermissions, ABC):

    def __init__(self, **kwargs):
        raw_settings = kwargs.get("settings", dict())
        WelcomeSettings.__init__(self, **raw_settings)
        LoggerSettings.__init__(self, **raw_settings)
        self.auto_moderation = AutoModerationSettings(self, **raw_settings)
        self.theme = ThemeSettings(self, **raw_settings)
        self.reactors = ReactorSettings(self, raw_settings.get("reactors", dict()))
        self.moderators = raw_settings.get("moderators", list())
        self.presets = raw_settings.get("presets", dict())
        self.roles = raw_settings.get("roles", dict())
        self.permissions = GuildPermissions(self, raw_settings.get("permissions", dict()))
        self.starboard = None
        if raw_starboard := raw_settings.get("starboard", dict()):
            self.__set_starboard(self.plugin.bot.get_channel(raw_starboard["channel_id"]), raw_starboard.get("count"))
        self.confessions_channel = self.plugin.bot.get_channel(raw_settings.get("confessions_channel"))
        self.verification = VerificationSettings(self, **raw_settings.get("verification", dict()))

    async def set_confessions_channel(self, channel):
        self.confessions_channel = channel

        self.collection.update_one(self.document_filter, {"$set": {"settings.confessions_channel": channel.id}})

    async def remove_confessions_channel(self):
        self.confessions_channel = None

        self.collection.update_one(self.document_filter, {"$unset": {"settings.confessions_channel": ""}})

    async def make_prime(self, make=True):
        self.is_prime = make

        await self.collection.update_one(
            self.document_filter, {"$set": {"is_prime": make}})

    def __set_starboard(self, channel, count=None):
        count = count or self.plugin.data.settings.default_star_count
        self.starboard = GuildStarboard(channel, count)

    async def set_starboard(self, channel, count):
        self.__set_starboard(channel, count)
        payload = {"channel_id": channel.id}
        if count and count != self.plugin.data.settings.default_star_count:
            payload["count"] = count
        await self.collection.update_one(
            self.document_filter, {"$set": {"settings.starboard": payload}}
        )

    async def remove_starboard(self):
        self.starboard = None
        await self.collection.update_one(
            self.document_filter, {"$unset": {"settings.starboard": ""}}
        )

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
