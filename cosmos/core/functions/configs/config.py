class Config(object):

    def __init__(self, config):
        self.raw = config
        for config in self.raw:
            if self.raw[config] == "":
                self.raw[config] = None
            self.__setattr__(config, self.raw[config])
