from abc import ABC, abstractmethod


class UserExperience(ABC):

    @property
    @abstractmethod
    def bot(self):
        raise NotImplementedError

    def __init__(self):
        pass
