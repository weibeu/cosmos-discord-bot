from abc import ABC

from .level import UserLevel
from .experience import UserExperience


class CosmosUserProfile(UserLevel, UserExperience, ABC):

    def __int__(self):
        self.id: int = None
