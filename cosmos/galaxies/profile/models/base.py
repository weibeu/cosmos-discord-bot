from abc import ABC, abstractmethod


class ProfileModelsBase(ABC):

    @property
    @abstractmethod
    def bot(self):
        raise NotImplementedError
