from abc import ABC, abstractmethod


class ProfileModelsBase(ABC):

    @property
    @abstractmethod
    def _plugin(self):
        raise NotImplementedError
