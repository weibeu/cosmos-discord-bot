from collections import UserString


class StaticProgressBar(UserString):

    PREFIX = "`|"
    SUFFIX = "|`"
    BASE = "▢"
    FILL = "▣"

    DEFAULT_WIDTH = 40

    def __init__(self, value, max_value, width=DEFAULT_WIDTH):
        if value > max_value:
            raise ValueError
        progress = self.FILL * round((value/max_value)*width)
        base = self.BASE * (width - len(progress))
        progress_bar = self.PREFIX + progress + base + self.SUFFIX
        super().__init__(progress_bar)
