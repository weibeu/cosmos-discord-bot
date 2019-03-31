from . import configs


class ConfigHandler(object):

    def __init__(self):
        self.__fetch_configs()

    def __fetch_configs(self):
        for string in dir(configs):
            attr = getattr(configs, string)
            if hasattr(attr, "NAME") and hasattr(attr, "PATH") and (attr.PATH or attr.NAME):
                self.__setattr__(attr.NAME, attr())
