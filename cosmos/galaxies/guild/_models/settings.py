from abc import ABC

from .base import CosmosGuildBase


class GuildSettings(CosmosGuildBase, ABC):

    def __init__(self, **kwargs):
        # raw_settings = kwargs.get("settings", dict())
        pass
