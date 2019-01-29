from abc import ABC, abstractmethod


class UserLevel(ABC):

    @property
    @abstractmethod
    def bot(self):
        raise NotImplementedError

    def __init__(self):
        pass
