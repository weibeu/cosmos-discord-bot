from .eminakoju import EminaKoju


class UsersCustomCommands(EminaKoju, ):
    """A plugin containing custom commands for our string tier patrons and supporters."""

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
