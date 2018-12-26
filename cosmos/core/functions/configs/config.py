import os
from abc import ABCMeta

from ...utilities import handlers


class Config(object):
    __metaclass__ = ABCMeta

    PATH = str()

    def __init__(self):
        self.raw = None
        self.PATH = os.path.join(self.PATH)
        self._fetch_config()

    def _fetch_config(self):
        self.raw = handlers.FileHandler.get_file_data(self.PATH)
        for config in self.raw:
            if self.raw[config] == "":
                self.raw[config] = None
            self.__setattr__(config, self.raw[config])
