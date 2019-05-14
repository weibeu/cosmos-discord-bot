from abc import ABC

from .base import CosmosGuildBase


class GuildLevels(CosmosGuildBase, ABC):

    def __init__(self, **kwargs):
        raw_levels = kwargs.get("levels", dict())
        roles = raw_levels.get("roles", list())
